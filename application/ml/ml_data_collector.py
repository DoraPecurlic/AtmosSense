import csv
import json
from datetime import datetime
from pathlib import Path
import paho.mqtt.client as mqtt
import argparse

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "atmosense/device-F401RE/telemetry"

PROJECT_ROOT = Path(__file__).resolve().parent
ML_DATA_DIR = PROJECT_ROOT/"data"/"ml"

LABELS = {
    "air": (
        "normal",
        "perfume",
        "alcohol",
        "heat",
    ),
    "light":(
        "dark",
        "daylight",
        "artificial",
    ),
}

FIELDS_NAMES =(
    "session_id",
    "domain",
    "label",
    "sequence_number",
    "stm_uptime_ms",
    "temperature_c",
    "humidity_percent",
    "pressure_hpa",
    "gas_resistance_ohm",
    "gas_valid",
    "heater_stable",
    "clear_raw",
    "red_raw",
    "green_raw",
    "blue_raw",
    "proximity_raw",
    "received_at",
)


class MLDataCollector:
    def __init__(self, domain: str, label: str) -> None:
        self._domain = domain
        self._label = label

        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._output_path = (ML_DATA_DIR/domain/label/f"{self._session_id}_{self._label}.csv")


        client_id = (f"atmosense-ml-{domain}-{self._session_id}")
        self._client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=mqtt.MQTTv5, )
        self._client.on_connect = self._subscribe
        self._client.on_message = self._save

        self._sample_count = 0
        self._csv_file = None
        self._writer = None



    def run(self) -> None:
        self._output_path.parent.mkdir(parents=True, exist_ok=True,) #napravi mape koje ne postoje, ako postoje samo nastavi

        with self._output_path.open(mode = "x",newline = "",encoding="utf-8",) as csv_file:
            self._csv_file = csv_file

            self._writer = csv.DictWriter(csv_file, fieldnames=FIELDS_NAMES)

            self._writer.writeheader()
            csv_file.flush()
            print("Starting ML data collection")
            print(f"Domain: {self._domain}")
            print(f"Label: {self._label}")
            print(f"Output file: {self._output_path}")

            try:
                self._client.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive = 60,)
                self._client.loop_forever()
            except KeyboardInterrupt:
                print("\nStopping ML data collection...")
            except OSError as error:
                raise ConnectionError("Could not connect to the MQTT broker") from error

            finally:
                self._client.disconnect()
                self._writer = None
                self._csv_file = None

        print(f"Collection finished. "f"Saved samples: {self._sample_count}")
        print(f"Saved file: {self._output_path}")


    def _subscribe(self, client, userdata,flags, reason_code, properties) -> None:
        if reason_code.is_failure:
            print(f"MQTT connestion failed: {reason_code}")
            return
    
        client.subscribe(MQTT_TOPIC, qos = 1)
        print(f"Subscribed to MQTT topic: {MQTT_TOPIC}")


    def _save(self, client, userdata, message) -> None:
        if self._writer is None:
            return

        if self._csv_file is None:
            return

        try:
            payload_text = message.payload.decode("utf-8")
            payload_data = json.loads(payload_text)

            sensor_values = {
                field_name: payload_data[field_name]
                for field_name in FIELDS_NAMES[3:]
            }

            row = {
                "session_id": self._session_id,
                "domain": self._domain,
                "label": self._label,
                **sensor_values,
            }

            self._writer.writerow(row)
            self._csv_file.flush()
            self._sample_count += 1

            if(self._sample_count == 1 or self._sample_count % 10 == 0):
                print(f"Saved samples: {self._sample_count}")


        except(UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, OSError, ) as error:
            print(f"Could not save MQTT sample: "f"{error}")

def parse_terminal_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect labeled ML data")
    parser.add_argument("domain", choices=LABELS.keys(), help="dataset type: air or light")
    parser.add_argument("label", help="Condition being recorded")
    arguments = parser.parse_args()

    allowed_labels = LABELS[arguments.domain]
    if arguments.label not in allowed_labels:
        parser.error("Invalid label for that domain.")

    return arguments


def main() -> None:

    arguments = parse_terminal_args()

    collector = MLDataCollector(domain=arguments.domain, label=arguments.label,)
    try:
        collector.run()
    except ConnectionError as error:
        print("Collector stoped.")

if __name__ == "__main__":
    main()

