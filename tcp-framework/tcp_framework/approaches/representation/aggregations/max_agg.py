from typing import Iterable
from .group_agg import GroupAgg


class MaxAgg(GroupAgg):
    def __call__(self, iterable: Iterable[float]) -> float:
        return max(iterable)
