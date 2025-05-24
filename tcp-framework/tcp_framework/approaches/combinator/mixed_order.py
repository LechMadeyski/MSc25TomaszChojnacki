from abc import abstractmethod
from collections.abc import Sequence
from typing import override

from ...datatypes import Ordering, RunContext, TestInfo
from ...deep import deepen
from ..approach import Approach


class MixedOrder(Approach):
    def __init__(self, targets: Sequence[Approach], weights: list[float] | None = None) -> None:
        self._targets = targets
        weights = weights if weights is not None else [1.0] * len(targets)
        assert len(targets) > 0, "targets must not be empty"
        assert len(weights) == len(targets), "targets and weights must have the same length"
        assert all(w >= 0 for w in weights), "weights must be non-negative"
        self._weights = [w / sum(weights) for w in weights]

    @abstractmethod
    def merge_queues(self, queues: list[Ordering]) -> Ordering: ...

    @override
    def prioritize(self, ctx: RunContext) -> None:
        queues = [
            target.get_dry_ordering(ctx) if weight > 0.0 else deepen(ctx.test_cases)
            for target, weight in zip(self._targets, self._weights, strict=True)
        ]
        for i, tcs in enumerate(self.merge_queues(queues)):
            for tc in tcs:
                ctx.execute(tc, key=str(i))

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for target in self._targets:
            target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        for target in self._targets:
            target.reset()
