
from pathlib import Path

from csv_storage import CsvStorage
from mqtt_publisher import MqttPublisher

from serial_connection import SerialConnection
from serial_protocol import SerialProtocol

from ml.air_predictor import AirPredictor
from ml.light_predictor import LightPredictor

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
   light_predictor = LightPredictor()
   last_sent_air_status = None
   last_sent_light_status = None

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

                air_status_for_display = None
                if air_prediction.status == "NORMAL":
                    air_status_for_display = "NORMAL"
                elif air_prediction.status == "AIR_CHANGE":
                    air_status_for_display ="DETECTED ANOMALY"

                if (air_status_for_display is not None and air_status_for_display != last_sent_air_status):
                    connection.write_line(f"AIR:{air_status_for_display}")

                    last_sent_air_status = air_status_for_display
                    print(
                        f"Sent to STM32: "
                        f"air:{air_status_for_display}"
                    )

           light_prediction = (light_predictor.add_reading(reading))
           if light_prediction is not None:
                print(
                    f"Light model: "
                    f"{light_prediction.status.upper()} | "
                    f"current window: "
                    f"{light_prediction.current_prediction.upper()} | "
                    f"confidence: "
                    f"{light_prediction.confidence:.2%} | "
                    f"votes: "
                    f"{light_prediction.winning_votes}/"
                    f"{light_prediction.history_size}"
                )

                light_status_for_dispay = light_prediction.status.upper()
                light_statuses = {
                    "DARK",
                    "DAYLIGHT",
                    "ARTIFICIAL",
                }
                if(light_status_for_dispay in light_statuses and light_status_for_dispay != last_sent_light_status):
                    connection.write_line(f"LIGHT:{light_status_for_dispay}")

                    last_sent_light_status = light_status_for_dispay
                    print(
                        f"Sent to STM32: "
                        f"LIGHT:{light_status_for_dispay}"
                    )
                

            
           
   except KeyboardInterrupt:
        print("\nStopping AtmosSense gateway...")

   finally:
        publisher.disconnect()
        connection.disconnect()


if __name__ == "__main__":
    main()