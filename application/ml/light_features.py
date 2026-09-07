import numpy as np
import pandas as pd

WINDOW_SIZE = 20
WINDOW_STEP = 5

MIN_CLEAR_FOR_COLOR_RATIOS = 50.0

REQUIRED_LIGHT_COLUMNS = (
    "clear_raw",
    "red_raw",
    "green_raw",
    "blue_raw",
)

LIGHT_FEATURE_NAMES = (
    "clear_log_mean",

    "red_clear_ratio_mean",

    "green_clear_ratio_mean",

    "blue_clear_ratio_mean",
)

def filter_valid_light_rows(data:pd.DataFrame) -> pd.DataFrame:
    missing_columns = []

    for column in REQUIRED_LIGHT_COLUMNS:
        if column not in data.columns:
            missing_columns.append(column)

    if missing_columns:
        raise ValueError("Missing columns")


    filtered_data = data.copy()
    for column in REQUIRED_LIGHT_COLUMNS:
        filtered_data[column] = pd.to_numeric(filtered_data[column],  errors="coerce",)

    filtered_data = filtered_data.dropna(subset=REQUIRED_LIGHT_COLUMNS)

    for column in REQUIRED_LIGHT_COLUMNS:
        filtered_data = filtered_data[filtered_data[column] >= 0]

    return filtered_data.reset_index(drop=True)

def create_light_feature_row(window: pd.DataFrame) -> dict[str, float]:

    clear = window["clear_raw"].to_numpy(dtype=float)
    red = window["red_raw"].to_numpy(dtype=float)
    green = window["green_raw"].to_numpy(dtype=float)
    blue = window["blue_raw"].to_numpy(dtype=float)

    clear_log = np.log1p(clear)

    safe_clear = np.maximum(clear, 1.0)

    color_signal_is_reliable = (clear >= MIN_CLEAR_FOR_COLOR_RATIOS)

    #koliko je neka boja izrazena u ukupnoj svjetlosti 
    red_clear_ratio = np.where(color_signal_is_reliable,red/safe_clear, 0.0)
    green_clear_ratio = np.where(color_signal_is_reliable,green/safe_clear, 0.0)
    blue_clear_ratio = np.where(color_signal_is_reliable,blue/safe_clear, 0.0)

    return {
        "clear_log_mean": float(clear_log.mean()),
        "red_clear_ratio_mean": float( red_clear_ratio.mean()),
        "green_clear_ratio_mean": float(green_clear_ratio.mean()),
        "blue_clear_ratio_mean": float(blue_clear_ratio.mean()),

    }






    

def create_light_feature_table(data: pd.DataFrame, step_size: int = WINDOW_STEP) -> pd.DataFrame:

    valid_data = filter_valid_light_rows(data)

    feature_rows = []

    last_start_index = (len(valid_data) - WINDOW_SIZE + 1)
    for start_index in range(0,last_start_index, step_size):
        end_index = (start_index + WINDOW_SIZE)

        window = valid_data.iloc[start_index:end_index]

        feature_row = create_light_feature_row(window)

        feature_rows.append(feature_row)

    return pd.DataFrame(feature_rows, columns=LIGHT_FEATURE_NAMES)