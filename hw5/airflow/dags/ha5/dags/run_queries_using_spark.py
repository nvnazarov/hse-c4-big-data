import logging

from airflow.sdk import dag, task  # type: ignore

logger = logging.getLogger(__name__)


@dag(dag_id="run_queries_using_spark")
def run_queries_using_spark():
    from ha5.config import SPARK_CONNECTION_ID, SPARK_CONF, SPARK_MASTER, ICEBERG_SCHEMA
    from airflow.providers.apache.spark.hooks.spark_sql import SparkSqlHook  # type: ignore

    @task
    def q1():
        """
        Для каждого клиента вывести ФИО и общую сумму его кредитов,
        а также сумму по всем кредитам.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q1' "
                "USING csv "
                "SELECT "
                "   clients.id AS client_id, "
                "   clients.full_name AS client_full_name, "
                "   SUM(credits.amount) AS total_client_credits, "
                "   SUM(SUM(credits.amount)) OVER () AS total_credits "
                "FROM "
                "   clients "
                "JOIN "
                "   credits ON credits.client_id = clients.id "
                "GROUP BY "
                "   clients.id, clients.full_name;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q2():
        """
        Для каждого клиента вывести ФИО, id вклада и сумму вклада,
        а также максимальную сумму вклада клиента.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q2' "
                "USING csv "
                "SELECT "
                "   clients.id AS client_id, "
                "   clients.full_name AS client_full_name, "
                "   deposits.id AS deposit_id, "
                "   deposits.amount AS deposit_amount, "
                "   MAX(deposits.amount) OVER (PARTITION BY clients.id) AS max_client_deposit_amount "
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
        """
        Для каждой транзакции вывести id транзакции, ФИО отправителя
        и сумму перевода, а также среднюю сумму перевода по всем
        транзакциям отправителя.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q3' "
                "USING csv "
                "SELECT "
                "   transactions.id AS transaction_id, "
                "   clients.full_name AS client_full_name, "
                "   transactions.amount AS transaction_amount, "
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
        """
        Для каждого актива вывести id актива, ФИО владельца и количество,
        а также суммарное количество активов клиента.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q4' "
                "USING csv "
                "SELECT "
                "   actives.id AS active_id, "
                "   clients.full_name AS client_full_name, "
                "   actives.count AS active_count, "
                "   SUM(actives.count) OVER (PARTITION BY clients.id) AS total_client_actives "
                "FROM "
                "   actives "
                "JOIN "
                "   bank_accounts ON bank_accounts.id = actives.bank_account_id "
                "JOIN "
                "   clients ON clients.id = bank_accounts.client_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q5():
        """
        Для каждого клиента вывести ФИО и зарплату, а также ранг
        зарплаты в пределах его отрасли.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q5' "
                "USING csv "
                "SELECT "
                "   clients.full_name AS client_full_name, "
                "   profiles.salary AS client_salary, "
                "   profiles.work_area AS client_work_area, "
                "   DENSE_RANK() OVER (PARTITION BY profiles.work_area ORDER BY profiles.salary DESC) AS client_salary_rank "
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
        """
        Для каждого кредита вывести id кредита, ФИО клиента и сумму, а
        также порядковый номер кредита клиента.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q6' "
                "USING csv "
                "SELECT "
                "   credits.id AS credit_id, "
                "   clients.full_name AS client_full_name, "
                "   credits.amount AS credit_amount, "
                "   ROW_NUMBER() OVER (PARTITION BY credits.client_id ORDER BY credits.dt_opened, credits.id) AS index "
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
        """
        Для каждого вклада вывести id вклада, ФИО клиента и сумму, а
        также среднюю сумму вкладов по всем клиентам.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q7' "
                "USING csv "
                "SELECT "
                "   deposits.id AS deposit_id, "
                "   clients.full_name AS client_full_name, "
                "   deposits.amount AS deposit_amount, "
                "   (SELECT AVG(deposits.amount) FROM deposits) AS avg_deposit_amount "
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
        """
        Для каждой транзакции вывести id транзакции, тип счёта
        отправителя и сумму, а также кумулятивную сумму переводов
        где данный счёт был отправителем.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q8' "
                "USING csv "
                "SELECT "
                "   transactions.id AS transaction_id, "
                "   bank_accounts.type AS bank_account_type, "
                "   transactions.amount AS transaction_amount, "
                "   SUM(transactions.amount) OVER (PARTITION BY transactions.send_bank_account_id) as cum_amount "
                "FROM "
                "   transactions "
                "JOIN "
                "   bank_accounts ON bank_accounts.id = transactions.send_bank_account_id;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    @task
    def q9():
        """
        Для каждого клиента вывести ФИО и процент по кредиту, а также
        минимальный процент среди всех кредитов клиента.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q9' "
                "USING csv "
                "SELECT "
                "   clients.id AS client_id, "
                "   clients.full_name AS client_full_name, "
                "   credits.percent AS credit_percent, "
                "   MIN(CAST(credits.percent AS NUMERIC(3,2))) OVER (PARTITION BY clients.id) AS min_client_percent "
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
    def q10():
        """
        Для каждой выплаты по кредиту вывести id выплаты и сумму выплаты,
        а также максимальную выплату по кредиту.
        """

        SparkSqlHook(
            sql=(
                f"USE {ICEBERG_SCHEMA};"
                "INSERT OVERWRITE DIRECTORY 's3a://bank/results/q10' "
                "USING csv "
                "SELECT "
                "   credit_payments.id AS payment_id, "
                "   credit_payments.amount AS payment_amount, "
                "   MAX(credit_payments.amount) OVER (PARTITION BY credit_payments.credit_id) AS max_credit_payment "
                "FROM "
                "   credit_payments;"
            ),
            conn_id=SPARK_CONNECTION_ID,
            master=SPARK_MASTER,
            conf=SPARK_CONF,
            verbose=False,
        ).run_query()

    _ = [q1() >> q2() >> q3() >> q4() >> q5() >> q6() >> q7() >> q8() >> q9() >> q10()]


run_queries_using_spark()
