from sensor_reading import SensorReading

class SerialProtocolError(ValueError):
    pass

class SerialProtocol:
    DATA_MESSAGE_TYPE = "DATA"
    DATA_FIELD_COUNT = 14

    def parse(self, message: str) -> SensorReading:
        message = message.strip()

        if not message:
            raise SerialProtocolError("Serial message cannot be empty")

        fields = message.split(",")

        if fields[0] != self.DATA_MESSAGE_TYPE:
            raise SerialProtocolError(f"Unknown message type: {fields[0]}")

        if len(fields) != self.DATA_FIELD_COUNT:
             raise SerialProtocolError(f"Data message should contain {self.DATA_FIELD_COUNT}, but does not.")

        try:
            return SensorReading(
                sequence_number= int(fields[1]),
                stm_uptime_ms= int(fields[2]),
                temperature_c= float(fields[3]),
                humidity_percent=float(fields[4]),
                pressure_hpa=float(fields[5]),
                gas_resistance_ohm=float(fields[6]),
                gas_valid=int(fields[7]),
                heater_stable=int(fields[8]),
                clear_raw = int(fields[9]),
                red_raw = int(fields[10]),
                green_raw= int(fields[11]),
                blue_raw= int(fields[12]),
                proximity_raw= int(fields[13])
            )
        except ValueError as error:
            raise SerialProtocolError("DATA message contains an invalid numeric value") from error