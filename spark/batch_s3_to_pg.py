import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, get_json_object, col

# Configuration
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "s3a://datalake/raw/")

PG_URL = os.getenv("PG_URL", "jdbc:postgresql://postgres:5432/telemetry_db")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_TABLE = "raw_telemetry"

def main():
    spark = SparkSession.builder \
        .appName("S3ToPostgresBatch") \
        .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # In a real production setup, we would read specific partitions (e.g. by passing date arguments)
    # For this architecture demonstration, we read the bucket
    # Note: Spark Streaming writes files with 'json_payload', 'kafka_timestamp', 'processed_at'

    try:
        df = spark.read.parquet(S3_BUCKET)
    except Exception as e:
        print(f"Failed to read from S3 (maybe bucket is empty?): {e}")
        sys.exit(0)

    # We extract topic and payload from json_payload to match the Postgres schema
    transformed_df = df \
        .withColumn("timestamp", col("kafka_timestamp")) \
        .withColumn("topic", get_json_object(col("json_payload"), "$.mqtt_topic")) \
        .withColumn("payload", get_json_object(col("json_payload"), "$.payload")) \
        .select("timestamp", "topic", "payload")

    # Write to Postgres via JDBC
    transformed_df.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", PG_TABLE) \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

    print("Successfully wrote batch to PostgreSQL.")

if __name__ == "__main__":
    main()
