import numpy as np
import pandas as pd


WINDOW_SIZE = 20
WINDOW_STEP = 5

REQUIRED_AIR_COLUMNS = (
    "temperature_c",
    "humidity_percent",
    "pressure_hpa",
    "gas_resistance_ohm",
    "gas_valid",
    "heater_stable",
)

AIR_FEATURE_NAMES = (
    "gas_log_mean",
    "gas_log_std",
    "gas_log_range",
    "gas_log_delta",
    "gas_log_slope",

    "temperature_mean",
    "temperature_std",
    "temperature_delta",

    "humidity_mean",
    "humidity_std",
    "humidity_delta",

    "pressure_mean",
    "pressure_std",
    "pressure_delta",
)

def filter_valid_air_rows(data: pd.DataFrame,) -> pd.DataFrame:
    missing_columns = []

    for column in REQUIRED_AIR_COLUMNS:
        if column not in data.columns:
            missing_columns.append(column)

    missing_text = ",".join(missing_columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_text}")

    filtered_data = data.copy()
    for column in REQUIRED_AIR_COLUMNS:
        filtered_data[column] = pd.to_numeric(filtered_data[column], errors="coerce") #errors="coerce" - pretvaranje vrijednostzi koja se ne moze pretvoriti u broj u Nan

    filtered_data = filtered_data.dropna(subset=REQUIRED_AIR_COLUMNS) # izbacivanje vrijednosti koje su nan

    filtered_data = filtered_data[(filtered_data["gas_valid"]==1) & (filtered_data["heater_stable"]==1) & (filtered_data["gas_resistance_ohm"] > 0 ) ]

    #vracanje pandas tablice koja je filtirana i ima indekse po redu (uklanjanjem nekih redaka ukloni se i indeks)
    return filtered_data.reset_index(drop=True)


def calculate_slope(values:np.ndarray) -> float:
    sample_positions = np.arange(len(values), dtype=float)
    slope = np.polyfit(sample_positions, values, 1)[0]
    return float(slope)

def create_air_feature_row( window: pd.DataFrame,) -> dict[str, float]:
    gas_resistance = window["gas_resistance_ohm"].to_numpy(dtype=float)
    gas_log = np.log1p(gas_resistance)

    temperature = window["temperature_c"].to_numpy(dtype=float)

    humidity = window["humidity_percent"].to_numpy(dtype=float)

    pressure = window["pressure_hpa"].to_numpy(dtype= float)

    return {
        "gas_log_mean": float(gas_log.mean()),
        "gas_log_std": float(gas_log.std()),
        "gas_log_range": float(gas_log.max() - gas_log.min()),
        "gas_log_delta": float(gas_log[-1] - gas_log[0]),
        "gas_log_slope": calculate_slope(gas_log),

        "temperature_mean": float(temperature.mean()),
        "temperature_std": float(temperature.std()),
        "temperature_delta": float(temperature[-1] - temperature[0]),

        "humidity_mean": float(humidity.mean()),
        "humidity_std": float(humidity.std()),
        "humidity_delta": float(humidity[-1] - humidity[0]),

        "pressure_mean": float(pressure.mean()),
        "pressure_std": float(pressure.std()),
        "pressure_delta": float(pressure[-1] - pressure[0]),

    }

def create_air_feature_table( data: pd.DataFrame, step_size = WINDOW_STEP) -> pd.DataFrame:

    #ciscenje podataka
    valid_data = filter_valid_air_rows(data)

    #spremanje izracunatih featura, svaki element jedan rijecnik-svaki rijecnik jedan prozor
    feature_rows = []

    last_start_index = (len(valid_data) - WINDOW_SIZE + 1)
    for start_index in range(0,last_start_index, step_size):
        end_index = (start_index + WINDOW_SIZE) 

        window = valid_data.iloc[start_index: end_index]
        feature_row = create_air_feature_row(window) 
        feature_rows.append(feature_row)


    return pd.DataFrame(feature_rows, columns=AIR_FEATURE_NAMES)

