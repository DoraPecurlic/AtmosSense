from pathlib import Path

import joblib
import numpy as np
import pandas as pd


from air_features import create_air_feature_table

ML_DIRECTORY = Path(__file__).resolve().parent

AIR_DATA_DIRECTORY = (ML_DIRECTORY/ "data"/ "ml"/ "air")
MODEL_PATH = (ML_DIRECTORY/ "models"/ "air_anomaly_model.joblib")

def main() -> None:
    model_artifact = joblib.load(MODEL_PATH)
    model = model_artifact["model"]
    feature_names = model_artifact["feature_names"]
    training_files = set( model_artifact["training_files"])

    label_directories = sorted(
        directory   
        for directory in AIR_DATA_DIRECTORY.iterdir()
        if directory.is_dir
    )



    print("AIR MODEL EVALUATION")
    for label_directory in label_directories:
        label = label_directory.name
        files = sorted(label_directory.glob("*.csv"))

        if label == "normal":
            evaluation_files = []
            for file in files:
                if file.name not in training_files:
                    evaluation_files.append(file)
            files = evaluation_files

        if not files:
            continue

        label_title = label.upper()
        print(label_title)

        anomaly_rates = []
        for file_path in files:
            session_anomaly_rate = evaluate_session(file_path,model,feature_names)
            anomaly_rates.append(session_anomaly_rate)

        average_anomaly_rate = np.mean(anomaly_rates)

        print(f"Average anomaly rate: " f"{average_anomaly_rate:.2f}%")



def evaluate_session(file_path: Path, model, feature_names: list[str]) -> float:
    sensor_data = pd.read_csv(file_path)
    feature_data = create_air_feature_table(sensor_data)
    if feature_data.empty:
        raise ValueError(f"No valid windows in {file_path.name}.")

    feature_data = feature_data[feature_names]
    predictions = model.predict(feature_data)

    anomaly_rate = calculate_anomaly_rate(predictions)

    print(
        f"{file_path.name}: "
        f"{len(sensor_data)} raw rows, "
        f"{len(feature_data)} windows, "
        f"{anomaly_rate:.2f}% anomalies"
    )

    return anomaly_rate


def calculate_anomaly_rate(predictions: np.ndarray,) -> float:

    anomaly_count = np.count_nonzero(predictions == -1)

    return (
        anomaly_count/len(predictions) * 100
    )


if __name__ == "__main__":
    main()