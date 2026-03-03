import logging

from airflow.sdk import dag  # type: ignore

logger = logging.getLogger(__name__)


@dag(dag_id="run_queries")
def run_queries():
    from ha5.config.postgres import POSTGRES_CONNECTION_ID

    from airflow.providers.common.sql.operators.sql import (
        SQLExecuteQueryOperator,  # type: ignore
    )

    _ = SQLExecuteQueryOperator(
        doc="Verify that the PostgreSQL database exists and is accessible.",
        task_id="check_postgresql_is_accessible",
        conn_id=POSTGRES_CONNECTION_ID,
        sql="SELECT 1;",
    )


run_queries()
