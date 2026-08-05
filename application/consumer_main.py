import os
from pathlib import Path

from dotenv import load_dotenv

from database_storage import DatabaseStorage
from database_consumer import DatabaseConsumer


ENV_FILE_PATH = (
    Path(__file__).resolve().parent.parent / ".env"
)

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "atmosense/device-F401RE/telemetry"


def get_required_environment_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(
            f"Missing environment variable: {name}"
        )

    return value


def main() -> None:
    load_dotenv(ENV_FILE_PATH)

    storage = DatabaseStorage(
        host=get_required_environment_variable(
            "POSTGRES_HOST"
        ),
        port=int(
            get_required_environment_variable(
                "POSTGRES_PORT"
            )
        ),
        database=get_required_environment_variable(
            "POSTGRES_DB"
        ),
        user=get_required_environment_variable(
            "POSTGRES_USER"
        ),
        password=get_required_environment_variable(
            "POSTGRES_PASSWORD"
        ),
    )

    consumer = DatabaseConsumer(
        host=MQTT_HOST,
        port=MQTT_PORT,
        topic=MQTT_TOPIC,
        storage=storage,
    )
    print("Connecting to PostgreSQL...", flush=True)
    storage.connect()
    print("Connected to PostgreSQL.", flush=True)

    try:
        print("Connecting to MQTT...", flush=True)
        consumer.connect()
        print("MQTT connection started.", flush=True)

        consumer.run()

    except KeyboardInterrupt:
        pass

    finally:
        consumer.disconnect()
        storage.disconnect()


if __name__ == "__main__":
    main()