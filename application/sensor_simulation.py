import time, random
from sensor_reading import SensorReading


class SensorSimulator:
    def __init__(self) -> None:
        self._sequence_number = 0
        self._start_time = time.monotonic()

    def _get_uptime_ms(self) -> int:
        elapsed_seconds = time.monotonic() - self._start_time
        return int(elapsed_seconds * 1000)

    def read(self) -> SensorReading:
        self._sequence_number += 1

        return SensorReading(
            sequence_number=self._sequence_number,
            stm_uptime_ms=self._get_uptime_ms(),
            temperature_c=round(random.uniform(22.0, 26.0), 2),
            humidity_percent=round(random.uniform(40.0, 60.0), 2),
            pressure_hpa=round(random.uniform(995.0, 1025.0), 2),
            gas_resistance_ohm=round(
                random.uniform(80000.0, 200000.0),
                2,
            ),
            clear_raw=random.randint(500, 1200),
            red_raw=random.randint(200, 600),
            green_raw=random.randint(200, 600),
            blue_raw=random.randint(200, 600),
            proximity_raw=random.randint(0, 30),
        )