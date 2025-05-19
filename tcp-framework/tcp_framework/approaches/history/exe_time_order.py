from collections import defaultdict
from typing import Sequence, override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach


class ExeTimeOrder(Approach):
    """
    Proposed. ?
    """

    def __init__(self, alpha: float = 0.8) -> None:
        self._times: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)
        self._alpha = alpha

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._times[tc]):
            ctx.execute(tc, key=f"{self._times[tc]:.3f}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for ti in test_infos:
            self._times[ti.case] = self._alpha * ti.result.time_s + (1.0 - self._alpha) * self._times[ti.case]

    @override
    def reset(self) -> None:
        self._times.clear()
