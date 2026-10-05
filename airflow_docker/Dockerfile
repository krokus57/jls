FROM apache/airflow:2.7.1-python3.10

USER root

# Install OpenJDK-11
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-11-jre-headless \
         procps \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

USER airflow

# Install Airflow providers and dbt dependencies
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.1.3 \
    dbt-core==1.6.5 \
    dbt-clickhouse==1.6.3 \
    pyspark==3.4.1
