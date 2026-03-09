import logging

from airflow.sdk import dag, task  # type: ignore

logger = logging.getLogger(__name__)


@dag(dag_id="seed_minio_with_csv_tables")
def seed_minio_with_csv_tables():
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
    def ensure_minio_bucket_exists(conn_id: str, bucket: str):
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
    def clear_minio_bucket_csv_tables(conn_id: str, bucket: str, key_prefix: str):
        from typing import Any, cast

        from ha5.core.iterutil import batched

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook  # type: ignore

        s3 = S3Hook(conn_id)
        bucket_keys = cast(list[Any], s3.list_keys(bucket, key_prefix))  # type: ignore
        if len(bucket_keys) == 0:
            logger.info(
                {
                    "msg": "the bucket is already empty",
                    "bucket": bucket,
                    "connection": conn_id,
                }
            )
            return
        logger.info(
            {
                "msg": "found objects in the bucket",
                "count": len(bucket_keys),
                "bucket": bucket,
                "connection": conn_id,
            }
        )
        for keys in batched(bucket_keys, 1000):
            s3.delete_objects(bucket, keys)  # type: ignore
            logger.info(
                {
                    "msg": "deleted objects from the bucket",
                    "count": len(keys),
                    "bucket": bucket,
                    "connection": conn_id,
                }
            )

    @task
    def put_csv_tables_into_minio_bucket(conn_id: str, bucket: str, key_prefix: str):
        from csv import DictWriter
        from io import StringIO
        from typing import Any, cast

        from ha5.core.seeder import Seeder

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook  # type: ignore

        s3 = S3Hook(conn_id)
        seeder = Seeder()
        database = seeder.generate_database()
        for table_name, entities in database.model_dump().items():
            entities = cast(list[dict[str, Any]], entities)
            if len(entities) == 0:
                logger.warning(
                    {
                        "msg": "the table is empty and will not be written to the minio",
                        "table_name": table_name,
                        "bucket": bucket,
                        "connection": conn_id,
                    }
                )
                continue
            buffer = StringIO()
            column_names = entities[0].keys()
            writer = DictWriter(buffer, column_names)
            writer.writeheader()
            writer.writerows([e for e in entities])
            key = f"{key_prefix}/{table_name}.csv"
            s3.load_string(buffer.getvalue(), key, bucket)  # type: ignore
            logger.info(
                {
                    "msg": "uploaded csv table to the minio",
                    "key": key,
                    "bucket": bucket,
                    "connection": conn_id,
                }
            )

    from ha5.config import (
        MINIO_CSV_BUCKET,
        MINIO_CONNECTION_ID,
        MINIO_CSV_KEY_PREFIX,
    )

    t1 = verify_minio_is_accessible(MINIO_CONNECTION_ID)
    t2 = ensure_minio_bucket_exists(MINIO_CONNECTION_ID, MINIO_CSV_BUCKET)
    t3 = clear_minio_bucket_csv_tables(
        MINIO_CONNECTION_ID, MINIO_CSV_BUCKET, MINIO_CSV_KEY_PREFIX
    )
    t4 = put_csv_tables_into_minio_bucket(
        MINIO_CONNECTION_ID, MINIO_CSV_BUCKET, MINIO_CSV_KEY_PREFIX
    )
    _ = t1 >> t2 >> t3 >> t4


seed_minio_with_csv_tables()
