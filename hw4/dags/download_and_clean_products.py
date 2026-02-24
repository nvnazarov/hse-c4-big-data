import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, TypeVar, cast

from airflow.providers.common.sql.operators.sql import (  # type: ignore
    SQLExecuteQueryOperator,
)
from airflow.providers.postgres.hooks.postgres import PostgresHook  # type: ignore
from airflow.sdk import dag  # type: ignore
from airflow.sdk import task  # type: ignore

logger = logging.getLogger(__name__)
POSTGRES_CONN_ID = "pg_conn"


@dataclass
class DirtyProduct:
    id: str
    url: str | None = None
    name: str | None = None
    price: str | None = None
    currency: str | None = None
    description: str | None = None


@dataclass
class Product:
    id: str
    url: str
    name: str
    price: float
    currency: str
    description: str | None = None


T = TypeVar("T")


def batched(i: Iterable[T], size: int):
    batch: list[T] = []
    for element in i:
        batch.append(element)
        if len(batch) == size:
            yield batch
            batch.clear()
    if batch:
        yield batch


@dag(dag_id="download_and_clean_products", schedule=timedelta(days=1))
def download_and_clean_products():
    check_database_is_accessible = SQLExecuteQueryOperator(
        doc="Checks that the database exists and is accessible.",
        task_id="check_database_is_accessible",
        conn_id=POSTGRES_CONN_ID,
        sql="SELECT 1;",
    )
    ensure_source_table_exists = SQLExecuteQueryOperator(
        doc="Ensures that the source table exists in the database.",
        task_id="ensure_source_table_exists",
        conn_id=POSTGRES_CONN_ID,
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
        conn_id=POSTGRES_CONN_ID,
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
    def download_products() -> str:
        """
        Loads the "dirty" products into the database. For now,
        this task just seeds the database with a random
        "dirty" products.
        """
        import random
        import uuid

        from psycopg2.extensions import cursor as PostgresCursor

        TABLE = "dirty_products"

        def random_str_or_none(str_p: float = 0.5) -> str | None:
            if not 0 < str_p <= 1:
                raise ValueError("probability must be in (0, 1] range")
            if random.uniform(0, 1) <= str_p:
                return uuid.uuid4().hex
            return None

        def random_float_or_none(float_p: float = 0.5) -> float | None:
            if not 0 < float_p <= 1:
                raise ValueError("probability must be in (0, 1] range")
            if random.uniform(0, 1) <= float_p:
                return random.uniform(100, 10000)
            return None

        def dirty_products_generator():
            while True:
                yield DirtyProduct(
                    id=uuid.uuid4().hex,
                    url=random_str_or_none(0.8),
                    name=random_str_or_none(0.8),
                    price=str(random_float_or_none(0.8)),
                    currency=random_str_or_none(0.8),
                    description=random_str_or_none(0.6),
                )

        def sql(x: str | None) -> str:
            return "NULL" if x is None else f"'{x}'"

        def compose_insert_stmt(products: list[DirtyProduct]) -> str:
            query = f"INSERT INTO {TABLE}(id, url, name, price, currency, description) VALUES\n"
            entries = list[str]()
            for product in products:
                entries.append(
                    f"({sql(product.id)}, {sql(product.url)}, {sql(product.name)}, {sql(product.price)}, {sql(product.currency)}, {sql(product.description)})"
                )
            query += ",\n".join(entries)
            query += (
                "\nON CONFLICT (id) DO UPDATE SET"
                "\n   url = EXCLUDED.url,"
                "\n   name = EXCLUDED.name,"
                "\n   price = EXCLUDED.price,"
                "\n   currency = EXCLUDED.currency,"
                "\n   description = EXCLUDED.description;"
            )
            return query

        count = 1000
        generator = dirty_products_generator()
        dirty_products = [next(generator) for _ in range(count)]
        logger.info({"msg": "generated dirty products", "count": len(dirty_products)})

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = hook.get_conn()
        cursor: PostgresCursor = conn.cursor()  # type: ignore
        batch_size = 100
        for products in batched(dirty_products, batch_size):
            cursor.execute(compose_insert_stmt(products))
            logger.info(
                {
                    "msg": "upserted a batch",
                    "size": len(products),
                    "inserted": cursor.rowcount,
                }
            )
        conn.commit()
        return TABLE

    @task
    def clean_products(dirty_table: str):
        """
        Transforms the "dirty" products into unified format and
        stores in the database.
        """
        from psycopg2.extensions import cursor as PostgresCursor

        MAX_DB_READ_REQUESTS = 1000
        CLEAN_TABLE = "products"

        def sql(x: str | float | int | None) -> str:
            if isinstance(x, int):
                return str(x)
            if isinstance(x, float):
                return str(x)
            return "NULL" if x is None else f"'{x}'"

        def compose_insert_stmt(products: Iterable[Product]) -> str:
            query = f"INSERT INTO {CLEAN_TABLE}(id, url, name, price, currency, description) VALUES\n"
            entries = list[str]()
            for product in products:
                entries.append(
                    f"({sql(product.id)}, {sql(product.url)}, {sql(product.name)}, {sql(product.price)}, {sql(product.currency)}, {sql(product.description)})"
                )
            query += ",\n".join(entries)
            query += (
                "\nON CONFLICT (id) DO UPDATE SET"
                "\n   url = EXCLUDED.url,"
                "\n   name = EXCLUDED.name,"
                "\n   price = EXCLUDED.price,"
                "\n   currency = EXCLUDED.currency,"
                "\n   description = EXCLUDED.description;"
            )
            return query

        def read_dirty_products_batched(batch_size: int):
            hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = hook.get_conn()
            cursor: PostgresCursor = conn.cursor()  # type: ignore
            last_id = ""
            for _ in range(MAX_DB_READ_REQUESTS):
                cursor.execute(
                    "SELECT id, url, name, price, currency, description "
                    f"FROM {dirty_table} "
                    f"WHERE id > {sql(last_id)}"
                    "ORDER BY id "
                    f"LIMIT {sql(batch_size)}"
                )
                products = [
                    DirtyProduct(
                        id=row[0],
                        url=row[1],
                        name=row[2],
                        price=row[3],
                        currency=row[4],
                        description=row[5],
                    )
                    for row in cursor.fetchall()
                ]
                if len(products) == 0:
                    break
                yield products
                last_id = products[-1].id
            conn.close()

        def clean_dirty_product(product: DirtyProduct) -> Product:
            if product.name is None:
                raise ValueError("name is none")
            if product.price is None:
                raise ValueError("price is none")
            if product.url is None:
                raise ValueError("url is none")
            if product.currency is None:
                raise ValueError("currency is none")
            return Product(
                id=product.id,
                url=product.url,
                name=product.name,
                price=float(product.price),
                currency=product.currency,
                description=product.description,
            )

        def save_cleaned_products(products: list[Product]) -> int:
            if len(products) == 0:
                return 0
            hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = hook.get_conn()
            cursor: PostgresCursor = conn.cursor()  # type: ignore
            cursor.execute(compose_insert_stmt(products))
            conn.commit()
            return cursor.rowcount

        batch_size = 100
        total_skipped = 0
        total_cleaned = 0
        total_written = 0
        for dirty_products_batch in read_dirty_products_batched(batch_size):
            logger.info(
                {
                    "msg": "processing dirty products batch",
                    "size": len(dirty_products_batch),
                }
            )
            cleaned_products = list[Product]()
            for dirty_product in dirty_products_batch:
                try:
                    product = clean_dirty_product(dirty_product)
                    cleaned_products.append(product)
                except ValueError as e:
                    total_skipped += 1
                    logger.info({"msg": "skipped dirty product", "reason": str(e)})
            total_cleaned += len(cleaned_products)
            total_written += save_cleaned_products(cleaned_products)
        logger.info(
            {
                "msg": "processed dirty products",
                "total_cleaned": total_cleaned,
                "total_skipped": total_skipped,
                "total_written": total_written,
            }
        )

    @task
    def clear_dirty_products(dirty_table: str):
        """
        Deletes processed dirty products.
        """
        from psycopg2.extensions import cursor as PostgresCursor

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = hook.get_conn()
        cursor: PostgresCursor = conn.cursor()  # type: ignore
        cursor.execute(f"DELETE FROM {dirty_table};")
        deleted_count = cursor.rowcount
        conn.commit()
        logger.info({"msg": "cleared dirty products", "count": deleted_count})

    t1 = check_database_is_accessible
    t2 = ensure_source_table_exists
    t3 = ensure_destination_table_exists
    t4 = download_products
    t5 = clean_products
    t6 = clear_dirty_products

    dirty_table = t4().as_setup()
    _ = t1 >> [t2, t3]
    _ = t2 >> dirty_table
    _ = t3 >> t5(cast(str, dirty_table)) >> t6(cast(str, dirty_table)).as_teardown()


download_and_clean_products()
