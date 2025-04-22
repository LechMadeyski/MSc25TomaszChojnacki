from collections import defaultdict
from typing import Optional, override
from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach


class BordaMixedOrder(Approach):
    def __init__(self, targets: list[Approach], weights: Optional[list[float]] = None) -> None:
        self._targets = targets
        weights = weights if weights is not None else [1.0] * len(targets)
        self._weights = [w / sum(weights) for w in weights]

    @override
    def prioritize(self, ctx: RunContext) -> None:
        queues = [target.get_dry_static_ordering(ctx) for target in self._targets]

        borda: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)
        for qi, queue in enumerate(queues):
            for ti, tc in enumerate(queue):
                borda[tc] += (len(queue) - ti - 1) * self._weights[qi]

        for tc in sorted(ctx.test_cases, key=lambda tc: borda[tc], reverse=True):
            ctx.execute(tc)

    @override
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        for target in self._targets:
            target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        for target in self._targets:
            target.reset()
