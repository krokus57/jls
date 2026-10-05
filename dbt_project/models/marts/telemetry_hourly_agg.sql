-- This is an analytical mart materialized as a MergeTree table in ClickHouse
-- It aggregates the data for faster querying by Superset

{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by=['topic', 'hour_bucket']
) }}

WITH staged AS (
    SELECT * FROM {{ ref('stg_telemetry') }}
)

SELECT
    topic,
    toStartOfHour(timestamp) AS hour_bucket,
    count(*) AS message_count,
    avg(metric_value) AS avg_metric_value,
    max(metric_value) AS max_metric_value,
    min(metric_value) AS min_metric_value
FROM staged
GROUP BY
    topic,
    hour_bucket
