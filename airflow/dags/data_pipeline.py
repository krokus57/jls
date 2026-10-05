from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 1. DAG for Spark Batch (S3 to PostgreSQL)
with DAG(
    's3_to_postgres_batch',
    default_args=default_args,
    description='A batch job to load raw telemetry from S3 to PostgreSQL',
    schedule_interval=timedelta(hours=1), # Run every hour
    catchup=False
) as dag1:

    # Note: In a real dockerized setup, we would submit to the Spark Master container
    # Here we mock the command for the architecture demonstration
    spark_batch = SparkSubmitOperator(
        task_id='submit_spark_batch',
        application='/opt/airflow/spark/batch_s3_to_pg.py',
        conn_id='spark_default', # Requires configuring connection in Airflow
        name='S3ToPostgresBatch',
        packages='org.postgresql:postgresql:42.6.0,org.apache.hadoop:hadoop-aws:3.3.4',
        verbose=True,
    )

# 2. DAG for dbt transformations (PostgreSQL -> ClickHouse)
with DAG(
    'dbt_clickhouse_transformations',
    default_args=default_args,
    description='Run dbt models to materialize data in ClickHouse',
    schedule_interval=timedelta(hours=1), # Typically runs after the Spark batch
    catchup=False
) as dag2:

    # We use a BashOperator to trigger dbt run in the dbt project directory
    run_dbt = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir .',
    )

    test_dbt = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt_project && dbt test --profiles-dir .',
    )

    run_dbt >> test_dbt
