from typing import Iterable
from .group_agg import GroupAgg


class AvgAgg(GroupAgg):
    def __call__(self, iterable: Iterable[float]) -> float:
        l = list(iterable)
        return sum(l) / len(l)
