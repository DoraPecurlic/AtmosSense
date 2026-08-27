CREATE TABLE IF NOT EXISTS measurements
(
    id BIGSERIAL PRIMARY KEY,

    sequence_number BIGINT NOT NULL,
    stm_uptime_ms BIGINT NOT NULL,

    temperature_c DOUBLE PRECISION NOT NULL,
    humidity_percent DOUBLE PRECISION NOT NULL,
    pressure_hpa DOUBLE PRECISION NOT NULL,
    gas_resistance_ohm DOUBLE PRECISION NOT NULL,

    gas_valid SMALLINT NOT NULL
        CHECK (gas_valid IN (0,1)),

    heater_stable SMALLINT NOT NULL
        CHECK (heater_stable IN (0,1)),

    clear_raw INTEGER NOT NULL,
    red_raw INTEGER NOT NULL,
    green_raw INTEGER NOT NULL,
    blue_raw INTEGER NOT NULL,
    proximity_raw INTEGER NOT NULL,

    received_at TIMESTAMPTZ NOT NULL,
    stored_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_measurements_received_at
ON measurements (received_at DESC);