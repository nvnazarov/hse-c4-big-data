import logging

from airflow.sdk import dag, task  # type: ignore

logger = logging.getLogger(__name__)


@dag(dag_id="run_queries_using_spark")
def run_queries_using_spark():
    from ha5.config import SPARK_CONNECTION_ID, SPARK_CONF, SPARK_MASTER, ICEBERG_SCHEMA
    from airflow.providers.apache.spark.hooks.spark_sql import SparkSqlHook  # type: ignore

    @task
    def q1():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q1' "
                "USING csv "
                "SELECT "
                "   clients.id, "
                "   clients.full_name, "
                "   SUM(credits.amount) AS total_credits "
                "FROM "
                "   clients "
                "JOIN "
                "   credits ON credits.client_id = clients.id "
                "GROUP BY clients.id, clients.full_name;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q2():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q2' "
                "USING csv "
                "SELECT "
                "   clients.id AS client_id, "
                "   clients.full_name, "
                "   deposits.id AS deposit_id, "
                "   deposits.amount, "
                "   MAX(deposits.amount) OVER (PARTITION BY clients.id) AS max_amount "
                "FROM "
                "   deposits "
                "JOIN "
                "   clients ON clients.id = deposits.client_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q3():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q3' "
                "USING csv "
                "SELECT "
                "   transactions.id, "
                "   clients.full_name, "
                "   transactions.amount, "
                "   AVG(transactions.amount) OVER (PARTITION BY clients.id) AS avg_amount "
                "FROM "
                "   transactions "
                "JOIN "
                "   bank_accounts ON bank_accounts.id = transactions.send_bank_account_id "
                "JOIN "
                "   clients ON clients.id = bank_accounts.client_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q4():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q4' "
                "USING csv "
                "SELECT "
                "   actives.id as active_id, "
                "   clients.full_name as owner_full_name, "
                "   actives.count, "
                "   SUM(actives.count) AS total_actives "
                "FROM "
                "   actives "
                "JOIN "
                "   bank_accounts ON bank_accounts.id = actives.bank_account_id "
                "JOIN "
                "   clients ON clients.id = bank_accounts.client_id "
                "GROUP BY actives.id, clients.full_name, actives.count;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q5():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q5' "
                "USING csv "
                "SELECT "
                "   clients.full_name, "
                "   profiles.salary, "
                "   profiles.work_area, "
                "   DENSE_RANK() OVER (PARTITION BY profiles.work_area ORDER BY profiles.salary DESC) AS salary_rank "
                "FROM "
                "   profiles "
                "JOIN "
                "   clients ON clients.id = profiles.client_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q6():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q6' "
                "USING csv "
                "SELECT "
                "   credits.id AS credit_id, "
                "   clients.full_name, "
                "   credits.amount, "
                "   ROW_NUMBER() OVER (PARTITION BY credits.client_id ORDER BY credits.dt_opened, credits.id) AS counter "
                "FROM "
                "   credits "
                "JOIN "
                "   clients ON clients.id = credits.client_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q7():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q7' "
                "USING csv "
                "SELECT "
                "   deposits.id AS deposit_id, "
                "   clients.full_name, "
                "   deposits.amount, "
                "   (SELECT AVG(deposits.amount) FROM deposits) AS avg_amount "
                "FROM "
                "   deposits "
                "JOIN "
                "   clients ON clients.id = deposits.client_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q8():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q8' "
                "USING csv "
                "SELECT "
                "   transactions.id AS transaction_id, "
                "   bank_accounts.type AS bank_account_type, "
                "   transactions.amount, "
                "   SUM(transactions.amount) as cum_amount "
                "FROM "
                "   transactions "
                "JOIN "
                "   bank_accounts ON bank_accounts.id = transactions.send_bank_account_id "
                "GROUP BY "
                "   transactions.id, "
                "   bank_accounts.type, "
                "   transactions.amount;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q9():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q9' "
                "USING csv "
                "SELECT "
                "   clients.id AS client_id, "
                "   clients.full_name, "
                "   credits.percent, "
                "   MIN(CAST(credits.percent AS NUMERIC(3,2))) AS min_percent "
                "FROM "
                "   credits "
                "JOIN "
                "   clients ON clients.id = credits.client_id "
                "GROUP BY "
                "   clients.id, clients.full_name, credits.id, credits.percent;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q10():
        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q10' "
                "USING csv "
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    _ = [q1() >> q2() >> q3() >> q4() >> q5() >> q6() >> q7() >> q8() >> q9() >> q10()]


run_queries_using_spark()
