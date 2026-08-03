from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SensorReading:
    sequence_number: int
    stm_uptime_ms: int

    temperature_c: float
    humidity_percent: float
    pressure_hpa: float
    gas_resistance_ohm: float

    clear_raw: int
    red_raw: int
    green_raw: int
    blue_raw: int
    proximity_raw: int


    recieved_at: datetime = field( default_factory=lambda: datetime.now().astimezone())