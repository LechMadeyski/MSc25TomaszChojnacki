from collections import defaultdict
from collections.abc import Sequence
from math import inf
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach

EPSILON = 1e-6


class FailDensityOrder(Approach):
    def __init__(self, *, alpha_fails: float = 0.8, alpha_exe: float = 0.4) -> None:
        assert 0.0 <= alpha_fails <= 1.0, "alpha_fails must be in the range [0, 1]"
        assert 0.0 <= alpha_exe <= 1.0, "alpha_exe must be in the range [0, 1]"

        self._alpha_fails = alpha_fails
        self._alpha_exe = alpha_exe

        self._fails: defaultdict[TestCase, float] = defaultdict(float)
        self._exe_s: defaultdict[TestCase, float] = defaultdict(float)

    def _density(self, tc: TestCase) -> float:
        if self._exe_s[tc] < EPSILON:
            return inf if self._fails[tc] > 0 else 0.0
        return self._fails[tc] / self._exe_s[tc]

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._density(tc), reverse=True):
            ctx.execute(tc, key=f"{self._density(tc):.3f}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for ti in test_infos:
            self._fails[ti.case] = (
                self._alpha_fails * ti.result.fails + (1.0 - self._alpha_fails) * self._fails[ti.case]
            )
            self._exe_s[ti.case] = self._alpha_exe * ti.result.time_s + (1.0 - self._alpha_exe) * self._exe_s[ti.case]

    @override
    def reset(self) -> None:
        self._fails.clear()
        self._exe_s.clear()
