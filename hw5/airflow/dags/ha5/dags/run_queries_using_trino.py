import logging

from airflow.sdk import dag, task  # type: ignore

logger = logging.getLogger(__name__)


@dag(dag_id="run_queries_using_trino")
def run_queries_using_trino():
    pass


run_queries_using_trino()
