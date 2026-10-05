-- This model reads from the ClickHouse external database pointing to PostgreSQL
-- and cleans/stages the data

{{ config(materialized='view') }}

WITH raw AS (
    SELECT
        id,
        timestamp,
        topic,
        payload
    FROM pg_external.raw_telemetry
)

SELECT
    id,
    timestamp,
    topic,
    payload,
    -- Extract specific metrics if payload is JSON
    -- Assuming a common "value" key inside the payload
    JSONExtractFloat(payload, 'value') as metric_value
FROM raw
WHERE payload IS NOT NULL
