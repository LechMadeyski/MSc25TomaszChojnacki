from random import Random
from typing import Optional, Sequence, override

from ...datatypes import TestCase
from ..approach import Approach
from .mixed_order import MixedOrder


class RandomMixedOrder(MixedOrder):
    """
    Proposed.
    """

    def __init__(self, targets: Sequence[Approach], weights: Optional[list[float]] = None, seed: int = 0) -> None:
        super().__init__(targets, weights)
        self._seed = seed
        self._rng = Random(seed)

    @override
    def merge_queues(self, queues: list[list[TestCase]]) -> list[TestCase]:
        result: list[TestCase] = []
        for _ in range(len(queues[0])):
            [i] = self._rng.choices(range(len(self._targets)), weights=self._weights)
            target = queues[i][0]
            for q in queues:
                q.remove(target)
            result.append(target)
        return result

    @override
    def reset(self) -> None:
        super().reset()
        self._rng.seed(self._seed)
