from airflow.sdk import dag  # type: ignore
from airflow.sdk import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator  # type: ignore


@dag(dag_id="load_products")
def load_products():
    ensure_source_table_exists = SQLExecuteQueryOperator(
        task_id="ensure_source_table_exists",
        conn_id="pg_conn",
        sql=(
            "CREATE TABLE IF NOT EXISTS dirty_products("
            "   id TEXT PRIMARY KEY, "
            "   url TEXT NOT NULL, "
            "   name TEXT, "
            "   description TEXT, "
            ")"
        ),
    )

    @task
    def ensure_destination_table_exists():
        """
        Ensures that the "processed" products table exists in
        the database.
        """
        pass

    @task
    def load_source_products():
        """
        Loads the "dirty" products into the database. For now,
        this task just seeds the database with a random
        products sample.
        """
        pass

    @task
    def process_products():
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

    t1 = ensure_source_table_exists
    t2 = ensure_destination_table_exists()
    t3 = load_source_products()
    t4 = process_products()
    _ = [t1, t2] >> t3 >> t4
