from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from ml.light_features import (
    WINDOW_SIZE,
    WINDOW_STEP,
    create_light_feature_table,
)
from sensor_reading import SensorReading


ML_DIRECTORY = Path(__file__).resolve().parent

DEFAULT_MODEL_PATH = (ML_DIRECTORY/"models"/"light_classifier.joblib")

LIGHT_STATUS_WARMING_UP = "WARMING_UP"

PREDICTION_HISTORY_SIZE = 3
VOTES_REQUIRED_FOR_CHANGE = 2

@dataclass(frozen=True)
class LightPrediction:
    status: str
    current_prediction: str
    confidence: float
    winning_votes: int
    history_size: int



class LightPredictor:
    def __init__(self,model_path: Path = DEFAULT_MODEL_PATH,) -> None:
        if not model_path.exists():
            raise FileNotFoundError(f"Light model was not found: {model_path}")

        model_artifact = joblib.load(model_path)

        self._model = model_artifact["model"]

        self._feature_names = list(model_artifact["feature_names"])

        self._readings = deque(maxlen=WINDOW_SIZE)

        self._recent_predictions = deque(maxlen=PREDICTION_HISTORY_SIZE)

        self._readings_since_prediction = 0
        self._status = LIGHT_STATUS_WARMING_UP


    @staticmethod
    def _is_valid_reading(reading: SensorReading) -> bool:
        return (reading.clear_raw >= 0 and reading.red_raw >= 0 and reading.green_raw >= 0 and reading.blue_raw >= 0)


    @staticmethod
    def _create_row( reading: SensorReading) -> dict[str,int]:
        return {
            "clear_raw": reading.clear_raw,
            "red_raw": reading.red_raw,
            "green_raw": reading.green_raw,
            "blue_raw": reading.blue_raw
        }

    def add_reading(self, reading: SensorReading) -> LightPrediction:
        if not self._is_valid_reading(reading):
            return None

        self._readings.append(self._create_row(reading))

        self._readings_since_prediction += 1

        if len(self._readings) < WINDOW_SIZE:
            return None
        if self._readings_since_prediction < WINDOW_STEP:
            return None

        self._readings_since_prediction = 0
        reading_table = pd.DataFrame(list(self._readings))

        feature_table = create_light_feature_table(reading_table)

        if feature_table.empty:
            return None

        model_input = feature_table.loc[:, self._feature_names]
        current_prediction = str(self._model.predict(model_input)[0])

        probabilities = (self._model.predict_proba(model_input)[0])

        confidence = float(probabilities.max())

        self._recent_predictions.append(current_prediction)

        vote_counts = Counter(self._recent_predictions)

        winning_label, winning_votes = (vote_counts.most_common(1)[0])

        if self._status == LIGHT_STATUS_WARMING_UP:
            self._status = current_prediction

        elif winning_votes >= VOTES_REQUIRED_FOR_CHANGE:
            self._status = winning_label

        return LightPrediction(
            status=self._status,
            current_prediction=current_prediction,
            confidence=confidence,
            winning_votes=winning_votes,
            history_size=len(
                self._recent_predictions
            ),
        )






