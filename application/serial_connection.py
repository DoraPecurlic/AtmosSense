import serial

class SerialConnection:
    def __init__(self, port: str, baud_rate:int = 115200,timeout: float = 2.0,) -> None:
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial: serial.Serial | None = None

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def connect(self) -> None:
        if self.is_connected:
            return
        try:
            self._serial = serial.Serial(
                port = self._port,
                baudrate =self._baud_rate,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout = self._timeout
            ) #8n1 format

        except serial.SerialException as error:
            self._serial = None

            raise ConnectionError(f"Could not open serial port {self._port}") from error

    def read_line(self) -> str:
        if not self.is_connected or self._serial is None:
            raise ConnectionError("Serial connection is not open")

        raw_message = self._serial.readline()
      
        return raw_message.decode("ascii").rstrip("\r\n")
    
    def disconnect(self) -> None:
        if self._serial is not None and self._serial.is_open:
            self._serial.close()

        self._serial = None


