ARG AIRFLOW__IMAGE__TAG=3.1.7

# Builds Airflow with all necessary dependencies.
FROM apache/airflow:${AIRFLOW__IMAGE__TAG}

# Specific Python libs are required to run
# Spark, e.g. pyspark. 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Java is required to run Spark operations.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless \
    && apt-get clean
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
