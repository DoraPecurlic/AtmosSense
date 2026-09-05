
from pathlib import Path

from csv_storage import CsvStorage
from mqtt_publisher import MqttPublisher

from serial_connection import SerialConnection
from serial_protocol import SerialProtocol

from ml.air_predictor import AirPredictor

DATA_FILE_PATH_CSV = (Path(__file__).resolve().parent.parent /"data" /"measurements.csv")

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "atmosense/device-F401RE/telemetry"

COM_PORT = "COM7"
BAUD_RATE = 115200

def main() -> None:
   connection  = SerialConnection(port = COM_PORT, baud_rate = BAUD_RATE)

   parser = SerialProtocol()

   storage = CsvStorage(DATA_FILE_PATH_CSV)

   publisher = MqttPublisher(host = MQTT_HOST, port = MQTT_PORT , topic = MQTT_TOPIC)


   air_predictor = AirPredictor()

   connection.connect()

   

   try:
       publisher.connect()

       while True:
           try:
               raw_message = connection.read_line()
               reading = parser.parse(raw_message)
           except TimeoutError:
                print("No serial message received, waiting...")
                continue
           
           storage.save(reading)
           publisher.publish(reading)
           print(f"Reading #{reading.sequence_number} "f"saved and published.")

           air_prediction = (air_predictor.add_reading(reading))

           if air_prediction is not None:
                window_result = ("ANOMALY" if air_prediction.current_window_is_anomaly else "NORMAL")

                print(
                    f"Air model: {air_prediction.status} | "
                    f"current window: {window_result} | "
                    f"score: "
                    f"{air_prediction.anomaly_score:.4f} | "
                    f"recent anomalies: "
                    f"{air_prediction.anomaly_votes}/"
                    f"{air_prediction.history_size}"
                )
           
   except KeyboardInterrupt:
        print("\nStopping AtmosSense gateway...")

   finally:
        publisher.disconnect()
        connection.disconnect()


if __name__ == "__main__":
    main()