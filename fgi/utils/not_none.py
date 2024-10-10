from typing import Optional, TypeVar

T = TypeVar("T")


def not_none(obj: Optional[T]) -> T:
    assert obj is not None
    return obj
