from typing import Iterable, TypeVar

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
