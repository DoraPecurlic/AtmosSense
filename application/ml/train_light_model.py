from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from light_features import (
    LIGHT_FEATURE_NAMES,
    create_light_feature_table,
)

ML_DIRECTORY = Path(__file__).resolve().parent
LIGHT_DATA_DIRECTORY = (ML_DIRECTORY/"data"/"ml"/"light")
MODEL_DIRECTORY = ML_DIRECTORY/"models"

MODEL_PATH = (MODEL_DIRECTORY / "light_classifier.joblib")

LIGHT_LABELS = (
    "dark",
    "daylight",
    "artificial",
)

def load_light_session(file_path: Path,) -> tuple[int, pd.DataFrame]:
    data = pd.read_csv(file_path)
    feature_table = create_light_feature_table(data)
    if feature_table.empty:
        raise ValueError( f"Not enough valid data in {file_path.name}")

    return len(data), feature_table

def main() -> None:
    training_feature_tables = []
    training_labels = []
    training_files = []

    validation_feature_tables = []
    validation_labels = []
    validation_files = []

    print("LIGHT MODEL TRAINING")
    print("\nTraining sessions:")

    for label in LIGHT_LABELS:
        label_directory =  LIGHT_DATA_DIRECTORY/label

        files = sorted(label_directory.glob("*.csv"))

        label_training_files = files[:-1]
        label_validation_file = files[-1]

        for file_path in label_training_files:
            raw_row_count, feature_table = ( load_light_session(file_path))
            training_feature_tables.append(feature_table)

            training_labels.extend([label] * len(feature_table)) #jer je supervised ucenje 

            training_files.append(file_path.name)

            print(
                f"{file_path.name}: "
                f"{raw_row_count} raw rows, "
                f"{len(feature_table)} windows"
            )

            raw_row_count, feature_table = (load_light_session(label_validation_file))
            validation_feature_tables.append(feature_table)
            validation_labels.extend([label] * len(feature_table))
            validation_files.append(label_validation_file.name)

    training_features = pd.concat(training_feature_tables,ignore_index=True,)

    validation_features = pd.concat(validation_feature_tables,ignore_index=True,)

    print("\nValidation sessions:")

    for file_name in validation_files:
        print(file_name)

    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(training_features,training_labels,)

    training_predictions = model.predict(training_features)
    validation_predictions = model.predict(validation_features)

    training_accuracy = accuracy_score(training_labels,training_predictions,)
    validation_accuracy = accuracy_score(validation_labels,validation_predictions,)
    print(f"\nTraining accuracy: "f"{training_accuracy:.2%}")
    print(f"Validation accuracy: "f"{validation_accuracy:.2%}")

    print("\nValidation classification report:")
    print(classification_report(validation_labels,validation_predictions,labels=LIGHT_LABELS,zero_division=0,))
    matrix = confusion_matrix(validation_labels,validation_predictions,labels=LIGHT_LABELS,)

    matrix_table = pd.DataFrame(matrix,index=[f"actual_{label}" for label in LIGHT_LABELS],
        columns=[f"predicted_{label}" for label in LIGHT_LABELS],
    )

    print("Validation confusion matrix:")
    print(matrix_table)

    MODEL_DIRECTORY.mkdir(parents=True,exist_ok=True,)

    model_artifact = {
        "model": model,
        "feature_names": list(LIGHT_FEATURE_NAMES),
        "training_files": training_files,
        "validation_files": validation_files,
        "labels": list(LIGHT_LABELS),
    }

    joblib.dump(model_artifact,MODEL_PATH,)

    print(f"\nModel saved to: {MODEL_PATH}")




if __name__ == "__main__":
    main()