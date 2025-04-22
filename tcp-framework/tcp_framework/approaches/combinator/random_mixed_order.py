from random import Random
from typing import Optional, override
from ...datatypes import RunContext, TestInfo
from ..approach import Approach


class RandomMixedOrder(Approach):
    def __init__(self, targets: list[Approach], weights: Optional[list[float]] = None, seed: int = 0) -> None:
        self._targets = targets
        weights = weights if weights is not None else [1.0] * len(targets)
        self._weights = [w / sum(weights) for w in weights]
        self._seed = seed
        self._rng = Random(seed)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        queues = [target.get_dry_static_ordering(ctx) for target in self._targets]
        for _ in range(len(ctx.test_cases)):
            [i] = self._rng.choices(range(len(self._targets)), weights=self._weights)
            target = queues[i][0]
            for q in queues:
                q.remove(target)
            ctx.execute(target)

    @override
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        for target in self._targets:
            target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._rng.seed(self._seed)
        for target in self._targets:
            target.reset()
