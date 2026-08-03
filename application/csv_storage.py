import csv
from pathlib import Path
from dataclasses import asdict

from sensor_reading import SensorReading


class CsvStorage:
    def __init__(self, file_path: str ) -> None:
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, reading: SensorReading) -> None:
        row = asdict(reading) # data klasu pretvara u rijecnik

        row["recieved_at"] = reading.recieved_at.strftime("%Y-%m-%d %H:%M:%S")

        file_has_data = (self._file_path.exists() and self._file_path.stat().st_size > 0)

        with self._file_path.open(mode = "a",newline = "",encoding="utf-8",) as file:
            writer = csv.DictWriter(file, fieldnames=row.keys())

            if not file_has_data:
                writer.writeheader()

            writer.writerow(row)

