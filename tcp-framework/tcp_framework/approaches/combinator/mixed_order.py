from abc import abstractmethod
from typing import Optional, override
from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach


class MixedOrder(Approach):
    def __init__(self, targets: list[Approach], weights: Optional[list[float]] = None) -> None:
        self._targets = targets
        weights = weights if weights is not None else [1.0] * len(targets)
        assert len(targets) > 0, "targets must not be empty"
        assert all(w > 0 for w in weights), "weights must be positive"
        assert len(weights) == len(targets), "targets and weights must have the same length"
        self._weights = [w / sum(weights) for w in weights]

    @abstractmethod
    def merge_queues(self, queues: list[list[TestCase]]) -> list[TestCase]: ...

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in self.merge_queues([target.get_dry_ordering(ctx) for target in self._targets]):
            ctx.execute(tc)

    @override
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        for target in self._targets:
            target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        for target in self._targets:
            target.reset()
