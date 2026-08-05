import psycopg

from sensor_reading import SensorReading


class DatabaseStorage:
    _INSERT_QUERY = """
        INSERT INTO measurements
        (
            sequence_number,
            stm_uptime_ms,
            temperature_c,
            humidity_percent,
            pressure_hpa,
            gas_resistance_ohm,
            clear_raw,
            red_raw,
            green_raw,
            blue_raw,
            proximity_raw,
            received_at
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """

    def __init__(self, host: str, port: str, database: str, user: str, password: str) -> None:
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

        self._connection: psycopg.Connection | None = None
    
    @property
    def is_connected(self) -> bool:
        return (self._connection is not None and not self._connection.closed)
    
    def connect(self) -> None:
        if self.is_connected:
            return

        try:
           self._connection = psycopg.connect(host = self._host, port = self._port, dbname = self._database, user = self._user, password = self._password)  

        except psycopg.Error as error:
            raise ConnectionError("Unable to connect to PostgreSQL") from error



    
    def save(self, reading: SensorReading) -> None:
        if not self.is_connected:
            raise ConnectionError( "PostgreSQL connection is not open")

        values = (
            reading.sequence_number,
            reading.stm_uptime_ms,
            reading.temperature_c,
            reading.humidity_percent,
            reading.pressure_hpa,
            reading.gas_resistance_ohm,
            reading.clear_raw,
            reading.red_raw,
            reading.green_raw,
            reading.blue_raw,
            reading.proximity_raw,
            reading.received_at,
        )

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(self._INSERT_QUERY, values)
            self._connection.commit()
        except psycopg.Error as error:
            raise RuntimeError("Could not save measurements to database")


    
    def disconnect(self) -> None:
        if self._connection is not None:
            if not self._connection.closed:
                self._connection.close()

            self._connection = None
    