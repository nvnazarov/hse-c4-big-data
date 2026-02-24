import pytest

from typing import Any


@pytest.mark.benchmark
def test_dag_loading(benchmark: Any):
    @benchmark
    def import_dag():  # type: ignore
        import dags.download_and_clean_products  # type: ignore # noqa: F401
