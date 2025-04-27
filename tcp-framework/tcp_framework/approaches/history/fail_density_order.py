from collections import defaultdict
from typing import override
from math import inf
from ..approach import Approach
from ...datatypes import RunContext, TestCase, TestInfo

EPSILON = 1e-6


class FailDensityOrder(Approach):
    """
    Proposed. ?
    """

    def __init__(self) -> None:
        self._fails: defaultdict[TestCase, int] = defaultdict(lambda: 0)
        self._times: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)

    def _density(self, tc: TestCase) -> float:
        if self._times[tc] < EPSILON:
            return inf if self._fails[tc] > 0 else 0.0
        return self._fails[tc] / self._times[tc]

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._density(tc), reverse=True):
            ctx.execute(tc)

    @override
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        for ti in test_infos:
            self._fails[ti.case] += ti.result.fails
            self._times[ti.case] += ti.result.time_s

    @override
    def reset(self) -> None:
        self._fails.clear()
        self._times.clear()
