CREATE DATABASE telemetry_db;

\c telemetry_db

CREATE TABLE IF NOT EXISTS raw_telemetry (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    topic VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_telemetry_timestamp ON raw_telemetry(timestamp);
CREATE INDEX idx_raw_telemetry_topic ON raw_telemetry(topic);
