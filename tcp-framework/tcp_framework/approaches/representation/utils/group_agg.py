from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import override


class GroupAgg(ABC):
    min: "GroupAgg"
    avg: "GroupAgg"
    max: "GroupAgg"

    @abstractmethod
    def __call__(self, iterable: Iterable[float]) -> float: ...


class _MinAgg(GroupAgg):
    @override
    def __call__(self, iterable: Iterable[float]) -> float:
        return min(iterable)


class _AvgAgg(GroupAgg):
    @override
    def __call__(self, iterable: Iterable[float]) -> float:
        collected = list(iterable)
        return sum(collected) / len(collected)


class _MaxAgg(GroupAgg):
    @override
    def __call__(self, iterable: Iterable[float]) -> float:
        return max(iterable)


GroupAgg.min = _MinAgg()
GroupAgg.avg = _AvgAgg()
GroupAgg.max = _MaxAgg()
