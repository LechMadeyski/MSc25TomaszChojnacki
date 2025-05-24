from collections import defaultdict
from collections.abc import Sequence
from math import inf
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach

EPSILON = 1e-6


class FailDensityOrder(Approach):
    def __init__(self, alpha: float = 0.8) -> None:
        self._alpha = alpha
        self._fails: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)
        self._times: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)

    def _density(self, tc: TestCase) -> float:
        if self._times[tc] < EPSILON:
            return inf if self._fails[tc] > 0 else 0.0
        return self._fails[tc] / self._times[tc]

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._density(tc), reverse=True):
            ctx.execute(tc, key=f"{self._density(tc):.3f}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for ti in test_infos:
            self._fails[ti.case] = self._alpha * ti.result.fails + (1.0 - self._alpha) * self._fails[ti.case]
            self._times[ti.case] = self._alpha * ti.result.time_s + (1.0 - self._alpha) * self._times[ti.case]

    @override
    def reset(self) -> None:
        self._fails.clear()
        self._times.clear()
