from collections import deque
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

import joblib
import pandas as pd


from ml.air_features import (
    WINDOW_SIZE,
    WINDOW_STEP,
    create_air_feature_table,
)
from sensor_reading import SensorReading




ML_DIRECTORY = Path(__file__).resolve().parent
MODEL_PATH = (ML_DIRECTORY / "models" / "air_anomaly_model.joblib")

AIR_STATUS_WARMING_UP = "WARMING_UP"
AIR_STATUS_NORMAL = "NORMAL"
AIR_STATUS_CHANGE = "AIR_CHANGE"

PREDICTION_HISTORY_SIZE = 5
ANOMALIES_REQUIRED_FOR_CHANGE = 2

@dataclass(frozen=True)
class AirPrediction:
    status: str
    current_window_is_anomaly: bool
    anomaly_score: float
    anomaly_votes: int
    history_size: int



class AirPredictor:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError("Air model not found")

        model_artifact = joblib.load(model_path)
        self._model = model_artifact["model"]
        self._feature_names = list(model_artifact["feature_names"])
        self._readings = deque(maxlen=WINDOW_SIZE)
        self._recent_anomalies = deque(maxlen=PREDICTION_HISTORY_SIZE)
        self._readings_since_prediction = 0
        self._status = AIR_STATUS_WARMING_UP


    @staticmethod
    def _create_row(reading:SensorReading) -> dict[str, float | int ]:
        return {
            "temperature_c": reading.temperature_c,
            "humidity_percent": reading.humidity_percent,
            "pressure_hpa": reading.pressure_hpa,
            "gas_resistance_ohm": reading.gas_resistance_ohm,
            "gas_valid": reading.gas_valid,
            "heater_stable": reading.heater_stable,
        }

    @staticmethod
    def _is_valid_reading(reading: SensorReading) -> bool:
        return (
            reading.gas_valid == 1 and reading.heater_stable == 1 and reading.gas_resistance_ohm > 0
        )


    def add_reading(self, reading: SensorReading) -> AirPrediction | None:
        if not self._is_valid_reading(reading):
            return None

        self._readings.append(self._create_row(reading))

        self._readings_since_prediction +=1

        if len(self._readings) < WINDOW_SIZE:
            return None

        if self._readings_since_prediction < WINDOW_STEP:
            return None

        self._readings_since_prediction = 0

        reading_table = pd.DataFrame(list(self._readings))

        feature_table = create_air_feature_table(reading_table)
        if feature_table.empty:
            return None

        model_input = feature_table.loc[:, self._feature_names] #uzmi sve retke iz tog stupca
        raw_prediction = int(self._model.predict(model_input)[0])
        anomaly_score = float(self._model.decision_function(model_input)[0])

        current_window_is_anomaly = (raw_prediction == -1)

        self._recent_anomalies.append(int(current_window_is_anomaly))
        anomaly_votes = sum(self._recent_anomalies)


        if self._status == AIR_STATUS_WARMING_UP:
            self._status = AIR_STATUS_NORMAL

        if(anomaly_votes >= ANOMALIES_REQUIRED_FOR_CHANGE):
            self._status = AIR_STATUS_CHANGE

        elif anomaly_votes == 0:
            self._status = AIR_STATUS_NORMAL

        return AirPrediction(
            status=self._status,
            current_window_is_anomaly=(current_window_is_anomaly),
            anomaly_score=anomaly_score,
            anomaly_votes=anomaly_votes,
            history_size=len(self._recent_anomalies),

        )
        
