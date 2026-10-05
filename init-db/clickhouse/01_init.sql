CREATE DATABASE IF NOT EXISTS analytical_db;

-- We configure an engine to read directly from PostgreSQL
-- This assumes postgres is reachable at host 'postgres', port 5432, db 'telemetry_db', user 'postgres', password 'postgres'
CREATE DATABASE IF NOT EXISTS pg_external
ENGINE = PostgreSQL('postgres:5432', 'telemetry_db', 'postgres', 'postgres', 'public');

-- This is where our dbt models will materialize data
CREATE DATABASE IF NOT EXISTS dbt_analytics;
