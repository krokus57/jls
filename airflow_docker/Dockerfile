FROM apache/airflow:2.10.2-python3.11

USER root

# Install OpenJDK-17 (Default for Debian 12 Bookworm)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-17-jre-headless \
         procps \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow

# Install Airflow providers and dbt dependencies
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.1.3 \
    dbt-core==1.6.5 \
    dbt-clickhouse==1.6.2 \
    pyspark==3.4.1
