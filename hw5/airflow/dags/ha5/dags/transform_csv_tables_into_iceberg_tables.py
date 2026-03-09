import logging

from airflow.sdk import dag, task  # type: ignore
from typing import Any


logger = logging.getLogger(__name__)


@dag(dag_id="transform_csv_tables_into_iceberg_tables")
def transform_csv_tables_into_iceberg_tables():
    @task
    def verify_minio_is_accessible(conn_id: str):
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook  # type: ignore

        s3 = S3Hook(conn_id)
        _ = s3.check_for_bucket("test")  # type: ignore
        logger.info(
            {
                "msg": "the minio is working as expected",
                "connection": conn_id,
            }
        )

    @task
    def ensure_iceberg_minio_bucket_exist(conn_id: str, bucket: str):
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook  # type: ignore

        s3 = S3Hook(conn_id)
        if s3.check_for_bucket(bucket):  # type: ignore
            logger.info(
                {
                    "msg": "the bucket already exsist",
                    "bucket": bucket,
                    "connection": conn_id,
                }
            )
            return
        s3.create_bucket(bucket)  # type: ignore
        logger.info(
            {
                "msg": "created the bucket",
                "bucket": bucket,
                "connection": conn_id,
            }
        )

    @task
    def verify_spark_is_accessible(
        conn_id: str,
        master: str,
        conf: dict[str, Any],
    ):
        from airflow.providers.apache.spark.hooks.spark_sql import SparkSqlHook  # type: ignore

        SparkSqlHook(
            "SELECT 1 as test;",
            conn_id=conn_id,
            master=master,
            conf=None,
            verbose=False,
        ).run_query()

    @task
    def transform_csv_tables_into_iceberg_tables(
        conn_id: str,
        master: str,
        conf: dict[str, Any],
        csv_bucket: str,
        csv_prefix: str,
        iceberg_schema: str,
    ):
        from ha5.core.seeder import Database
        from airflow.providers.apache.spark.hooks.spark_sql import SparkSqlHook  # type: ignore

        def compose_csv_to_iceberg_sql(table: str) -> str:
            return (
                f"CREATE OR REPLACE TEMPORARY VIEW {table}_view "
                "USING csv "
                "OPTIONS ("
                f"    path 's3a://{csv_bucket}/{csv_prefix}/{table}.csv',"
                "    header 'true',"
                "    inferSchema 'true',"
                "    delimiter ','"
                ");"
                f"CREATE OR REPLACE TABLE {iceberg_schema}.{table} "
                "USING iceberg "
                "AS "
                f"SELECT * FROM {table}_view;"
            )

        SparkSqlHook(
            sql=(f"CREATE SCHEMA IF NOT EXISTS {iceberg_schema};"),
            conn_id=conn_id,
            master=master,
            conf=conf,
            verbose=False,
        ).run_query()
        for table in Database.model_fields.keys():
            SparkSqlHook(
                sql=compose_csv_to_iceberg_sql(table),
                conn_id=conn_id,
                master=master,
                conf=conf,
                verbose=False,
            ).run_query()

    from ha5.config import (
        MINIO_CONNECTION_ID,
        MINIO_CSV_BUCKET,
        MINIO_CSV_KEY_PREFIX,
        MINIO_ICEBERG_BUCKET,
        ICEBERG_SCHEMA,
        SPARK_CONNECTION_ID,
        SPARK_MASTER,
        SPARK_CONF,
    )

    t1 = verify_minio_is_accessible(MINIO_CONNECTION_ID)
    t2 = ensure_iceberg_minio_bucket_exist(MINIO_CONNECTION_ID, MINIO_ICEBERG_BUCKET)
    t3 = verify_spark_is_accessible(SPARK_CONNECTION_ID, SPARK_MASTER, SPARK_CONF)
    t4 = transform_csv_tables_into_iceberg_tables(
        SPARK_CONNECTION_ID,
        SPARK_MASTER,
        SPARK_CONF,
        MINIO_CSV_BUCKET,
        MINIO_CSV_KEY_PREFIX,
        ICEBERG_SCHEMA,
    )
    _ = [t1 >> t2, t3] >> t4


transform_csv_tables_into_iceberg_tables()
