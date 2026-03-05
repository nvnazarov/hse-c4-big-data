import logging

from airflow.sdk import dag, task  # type: ignore
from typing import Any

logger = logging.getLogger(__name__)


@dag(dag_id="run_queries")
def run_queries():
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
    def ensure_iceberg_namespace_exists():
        pass

    @task
    def verify_spark_is_accessible(
        conn_id: str,
        master: str,
        conf: dict[str, Any] = dict(),
    ):
        from airflow.providers.apache.spark.hooks.spark_sql import SparkSqlHook  # type: ignore

        SparkSqlHook(
            "SELECT 1 as test;",
            conn_id=conn_id,
            master=master,
            conf=conf,
            verbose=False,
        ).run_query()

    @task
    def transform_csv_tables_into_iceberg_tables(
        conn_id: str,
        master: str,
        conf: dict[str, Any] = dict(),
    ):
        from ha5.config.spark import SPARK_CONNECTION_ID, SPARK_CONF
        from ha5.core.sql import compose_csv_to_iceberg_sql
        from airflow.providers.apache.spark.hooks.spark_sql import SparkSqlHook  # type: ignore

        SparkSqlHook(
            sql=("CREATE NAMESPACE IF NOT EXISTS bank.warehouse;"),
            conn_id=SPARK_CONNECTION_ID,
            master="spark://spark-master:7077",
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()
        SparkSqlHook(
            sql=compose_csv_to_iceberg_sql("clients"),
            conn_id=SPARK_CONNECTION_ID,
            master="spark://spark-master:7077",
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    from ha5.config.minio import MINIO_CONNECTION_ID, MINIO_ICEBERG_BUCKET
    from ha5.config.spark import SPARK_CONNECTION_ID, SPARK_CONF, SPARK_MASTER

    t1 = verify_minio_is_accessible(MINIO_CONNECTION_ID)
    t2 = ensure_iceberg_minio_bucket_exist(MINIO_CONNECTION_ID, MINIO_ICEBERG_BUCKET)
    t3 = verify_spark_is_accessible(SPARK_CONNECTION_ID, SPARK_MASTER, SPARK_CONF)
    t4 = transform_csv_tables_into_iceberg_tables(
        SPARK_CONNECTION_ID, SPARK_MASTER, SPARK_CONF
    )
    _ = [t1 >> t2, t3] >> t4


run_queries()
