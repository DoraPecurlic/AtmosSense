
from pathlib import Path

from csv_storage import CsvStorage
from mqtt_publisher import MqttPublisher

from serial_connection import SerialConnection
from serial_protocol import SerialProtocol

DATA_FILE_PATH_CSV = (Path(__file__).resolve().parent.parent /"data" /"measurements.csv")

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "atmosense/device-F401RE/telemetry"

COM_PORT = "COM7"
BAUD_RATE = "115200"

def main() -> None:
   connection  = SerialConnection(port = COM_PORT, baud_rate = BAUD_RATE)

   parser = SerialProtocol()

   storage = CsvStorage(DATA_FILE_PATH_CSV)

   publisher = MqttPublisher(host = MQTT_HOST, port = MQTT_PORT , topic = MQTT_TOPIC)

   connection.connect()

   

   try:
       publisher.connect()
       readings_received = 0

       while readings_received < 5:
           try:
               raw_message = connection.read_line()
               reading = parser.parse(raw_message)
           except TimeoutError:
                print("No serial message received, waiting...")
                continue
           
           storage.save(reading)
           publisher.publish(reading)
           readings_received += 1
       
           
   finally:
        publisher.disconnect()
        connection.disconnect()


if __name__ == "__main__":
    main()