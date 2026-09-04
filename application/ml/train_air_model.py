from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    StandardScaler,
)

from sklearn.ensemble import (
    IsolationForest,
)

from air_features import (
    AIR_FEATURE_NAMES,
    WINDOW_SIZE,
    WINDOW_STEP,
    create_air_feature_table,
)


ML_DIRECTORY = Path(__file__).resolve().parent
NORMAL_AIR_DIR = (ML_DIRECTORY/"data"/"ml"/"air"/"normal")
MODEL_DIRECTORY = (ML_DIRECTORY/"models")

MODEL_PATH = (MODEL_DIRECTORY/"air_anomaly_model.joblib")

def main() -> None:
    files = sorted(NORMAL_AIR_DIR.glob("*.csv"))

    training_files = files[:-1]
    validation_file = files[-1]

    print("Training sessions:")
    training_feature_tables = []

    for file in training_files:
        feature_table = load_session_features(file)
        training_feature_tables.append(feature_table)

    training_features = pd.concat(training_feature_tables, ignore_index=True)

    print("\nValidation session:")
    validation_features = load_session_features(validation_file)

    print(f"\nTotal training windows: " f"{len(training_features)}")
    print(f"\nTotal validation windows: " f"{len(validation_features)}")

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("Isolation_forest", 
             IsolationForest(n_estimators=300, contamination=0.03,random_state=42, n_jobs=-1)),
        ]
    )
    model.fit(training_features)

    training_predictions=model.predict(training_features)
    validation_predictions=model.predict(validation_features)

    training_anomaly_rate = (calculate_anomaly_rate(training_predictions))
    validation_anomaly_rate = (calculate_anomaly_rate(validation_predictions))
    print(f"\nTraining anomaly rate: " f"{training_anomaly_rate:.2f}%")
    print(f"\n Validation anomaly rate: " f"{validation_anomaly_rate:.2f}%")

    model_artifact = {
        "model": model,
        "feature_names": list(AIR_FEATURE_NAMES),
        "window_size": WINDOW_SIZE,
        "window_step": WINDOW_STEP,
        "training_files": [file.name for file in training_files],
        "validation_file":[validation_file.name,],
        "trained_at": datetime.now().isoformat(timespec="seconds"),
    }

    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_artifact, MODEL_PATH)
    print(f"\nModel saved to: "f"{MODEL_PATH}")



def load_session_features(file_path: Path) -> pd.DataFrame:
    sensor_data = pd.read_csv(file_path)

    feature_data = create_air_feature_table(sensor_data)

    if feature_data.empty:
        raise ValueError("Session empty.")

    print(f"{file_path.name}:"
          f"{len(sensor_data)} raw rows"
          f"{len(feature_data)} windows")

    return feature_data


def calculate_anomaly_rate(predictions: np.ndarray,) -> float:
    anomaly_count = np.count_nonzero(predictions == -1)
    return (anomaly_count/len(predictions) * 100)



if __name__ == "__main__":
    main()