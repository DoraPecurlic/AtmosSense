import json
from dataclasses import asdict

import paho.mqtt.client as mqtt

from sensor_reading import SensorReading

class MqttPublisher:
    def __init__(self, host:str, port: int, topic: str)->None:
        self._host = host
        self._port = port
        self._topic = topic

        self._client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="atmosense-edge-gateway", protocol=mqtt.MQTTv5)
    
    def connect(self) -> None:
        self._client.connect(host = self._host, port = self._port, keepalive = 60)

        self._client.loop_start() #odrzava mrezu za kontinuirwanu komunikaciju
    
    def publish(self, data: SensorReading) -> None:
        payload_data = asdict(data)

        payload_data["received_at"] = data.received_at.strftime("%Y-%m-%d %H:%M:%S")

        payload = json.dumps(payload_data)

        message = self._client.publish(topic = self._topic, payload=payload, qos = 1)

        if message.rc != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectionError(f"MQTT publish failed: {mqtt.error_string(message.rc)}")

        message.wait_for_publish(timeout=5.0)

        if not message.is_published():
            raise TimeoutError("MQTT message was not published in time")
    
    def disconnect(self)->None:
        self._client.disconnect()
        self._client.loop_stop()