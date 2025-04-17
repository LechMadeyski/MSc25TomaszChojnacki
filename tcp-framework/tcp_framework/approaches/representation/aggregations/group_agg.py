from typing import Protocol, Iterable


class GroupAgg(Protocol):
    def __call__(self, iterable: Iterable[float]) -> float:
        raise NotImplementedError
