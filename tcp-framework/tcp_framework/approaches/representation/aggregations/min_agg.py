from typing import Iterable
from .group_agg import GroupAgg


class MinAgg(GroupAgg):
    def __call__(self, iterable: Iterable[float]) -> float:
        return min(iterable)
