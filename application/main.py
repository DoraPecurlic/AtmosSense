import time
from pathlib import Path

from sensor_simulation import SensorSimulator
from csv_storage import CsvStorage
from mqtt_publisher import MqttPublisher

DATA_FILE_PATH_CSV = (Path(__file__).resolve().parent.parent /"data" /"measurements.csv")

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "atmosense/device-F401RE/telemetry"

def main() -> None:
   simulator = SensorSimulator()
   storage = CsvStorage(DATA_FILE_PATH_CSV)

   publisher = MqttPublisher(host = MQTT_HOST, port = MQTT_PORT , topic = MQTT_TOPIC)

   publisher.connect()

   try:
       for _ in range(5):
           reading = simulator.read()

           storage.save(reading)
           publisher.publish(reading)

           print(
                f"Reading #{reading.sequence_number} "
                f"saved to CSV and published to MQTT"
            )

           time.sleep(1)
           
   finally:
        publisher.disconnect()


if __name__ == "__main__":
    main()