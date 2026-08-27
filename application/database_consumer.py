#ssubscriba se na topic telemety,m primi reading, spremi pomocu database_storage.save u sql

import json
import paho.mqtt.client as mqtt

from datetime import datetime
from  database_storage import DatabaseStorage
from sensor_reading import SensorReading

class DatabaseConsumer:
    def __init__(self, host: str, port: int, topic: str, storage: DatabaseStorage) -> None:
        self._host = host
        self._port = port
        self._topic = topic
        self._storage = storage

        self._client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="atmosense-database-consumer", protocol=mqtt.MQTTv5, )
        
        self._client.on_connect = self._subscribe
        self._client.on_message = self._save


    def connect(self)-> None:
        self._client.connect(host = self._host, port = self._port)

    def run(self)-> None:
            self._client.loop_forever()

    def _subscribe(self, client, userdata,flags, reason_code, properties)-> None:

        if reason_code.is_failure:
            print(f"MQTT connestion failed: {reason_code}")
            return

        client.subscribe(self._topic, qos = 1)
        print(f"Subscribed to MQTT topic: {self._topic}")

    def _save(self, client, userdata, message)-> None:
        try:
             payload_text = message.payload.decode("utf-8")  #jer paho daje bajteve, a ne string
             payload_data = json.loads(payload_text) #iz jsona on vrati dict

             reading = self._create_reading(payload_data)
             self._storage.save(reading)
        except (ConnectionError, RuntimeError) as error:
            print(f"Could not store MQTT message: {error}")

    @staticmethod
    def _create_reading(payload_data: dict)->SensorReading:
         return SensorReading(
              sequence_number = int(payload_data["sequence_number"]),
              stm_uptime_ms = int(payload_data["stm_uptime_ms"]),

              temperature_c = float(payload_data["temperature_c"]),
              humidity_percent = float(payload_data["humidity_percent"]),
              pressure_hpa = float(payload_data["pressure_hpa"]),
              gas_resistance_ohm = float(payload_data["gas_resistance_ohm"]),

              gas_valid=int(payload_data["gas_valid"]),
              heater_stable=int(payload_data["heater_stable"]),

              clear_raw = int(payload_data["clear_raw"]),
              red_raw = int(payload_data["red_raw"]),
              green_raw = int(payload_data["green_raw"]),
              blue_raw = int(payload_data["blue_raw"]),
              proximity_raw = int(payload_data["proximity_raw"]),

              received_at = datetime.fromisoformat(payload_data["received_at"]),
            )
                       

    
    def disconnect(self)-> None:
        self._client.disconnect()