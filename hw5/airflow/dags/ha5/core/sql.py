from ha5.config.minio import MINIO_CSV_BUCKET


def compose_csv_to_iceberg_sql(table: str) -> str:
    return (
        f"CREATE OR REPLACE TEMPORARY VIEW {table}_view "
        "USING csv "
        "OPTIONS ("
        f"    path 's3a://{MINIO_CSV_BUCKET}/{table}.csv',"
        "    header 'true',"
        "    inferSchema 'true',"
        "    delimiter ','"
        ");"
        f"CREATE TABLE bank.warehouse.{table} "
        "USING iceberg "
        "AS "
        "SELECT * FROM clients_view;"
    )
