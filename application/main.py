import time
from pathlib import Path

from sensor_simulation import SensorSimulator
from csv_storage import CsvStorage

DATA_FILE_PATH_CSV = (Path(__file__).resolve().parent.parent /"data" /"measurements.csv")

def main() -> None:
   simulation = SensorSimulator()
   storage = CsvStorage(DATA_FILE_PATH_CSV)

   for _ in range(5):
       reading = simulation.read()
       storage.save(reading)
       time.sleep(1)

if __name__ == "__main__":
    main()