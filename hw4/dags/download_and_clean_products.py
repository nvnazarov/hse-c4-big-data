from airflow.sdk import dag  # type: ignore
from airflow.sdk import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator  # type: ignore


@dag(dag_id="download_and_clean_products")
def download_and_clean_products():
    check_database_is_accessible = SQLExecuteQueryOperator(
        doc="Checks that the database exists and is accessible.",
        task_id="check_database_is_accessible",
        conn_id="pg_conn",
        sql="SELECT 1;",
    )
    ensure_source_table_exists = SQLExecuteQueryOperator(
        doc="Ensures that the source table exists in the database.",
        task_id="ensure_source_table_exists",
        conn_id="pg_conn",
        sql=(
            "CREATE TABLE IF NOT EXISTS dirty_products("
            "   id TEXT PRIMARY KEY, "
            "   url TEXT, "
            "   name TEXT, "
            "   description TEXT, "
            "   price TEXT, "
            "   currency TEXT "
            ");"
        ),
    )
    ensure_destination_table_exists = SQLExecuteQueryOperator(
        doc="Ensures that the destination table exists in the database.",
        task_id="ensure_destination_table_exists",
        conn_id="pg_conn",
        sql=(
            "CREATE TABLE IF NOT EXISTS products("
            "   id TEXT PRIMARY KEY, "
            "   url TEXT NOT NULL, "
            "   name TEXT NOT NULL, "
            "   description TEXT, "
            "   price NUMERIC(7, 2) NOT NULL, "
            "   currency TEXT NOT NULL "
            ");"
        ),
    )

    @task
    def download_products():
        """
        Loads the "dirty" products into the database. For now,
        this task just seeds the database with a random
        "dirty" products sample.
        """
        pass

    @task
    def clean_products():
        """
        Transforms the "dirty" products into unified format and
        stores in the database.
        """
        # extract

        # transform

        # load

        # log:
        # 1. total rows processed
        # 2. columns
        # 3. result
        # 4. how many rows written
        pass

    t1 = check_database_is_accessible
    t2 = ensure_source_table_exists
    t3 = ensure_destination_table_exists
    t4 = download_products()
    t5 = clean_products()
    _ = t1 >> [t2, t3]
    _ = t2 >> t4 >> t5
    _ = t3 >> t5


download_and_clean_products()
