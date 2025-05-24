from collections.abc import Sequence
from random import Random
from typing import override

from ...datatypes import Ordering
from ...deep import deep_len, deep_remove
from ..approach import Approach
from .mixed_order import MixedOrder


class RandomMixedOrder(MixedOrder):
    """
    Proposed.
    """

    def __init__(self, targets: Sequence[Approach], weights: list[float] | None = None, seed: int = 0) -> None:
        super().__init__(targets, weights)
        self._seed = seed
        self._rng = Random(seed)

    @override
    def merge_queues(self, queues: list[Ordering]) -> Ordering:
        result: Ordering = []
        for _ in range(deep_len(queues[0])):
            [i] = self._rng.choices(range(len(self._targets)), weights=self._weights)
            target_group = queues[i][0]
            target = self._rng.choice(target_group)
            for q in queues:
                deep_remove(q, target)
            result.append([target])
        return result

    @override
    def reset(self) -> None:
        super().reset()
        self._rng.seed(self._seed)
