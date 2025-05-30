from collections import defaultdict
from collections.abc import Sequence
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach


class ExeTimeOrder(Approach):
    def __init__(self, alpha: float = 0.4) -> None:
        assert 0.0 <= alpha <= 1.0, "alpha must be in the range [0, 1]"

        self._exe_s: defaultdict[TestCase, float] = defaultdict(float)
        self._alpha = alpha

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._exe_s[tc]):
            ctx.execute(tc, key=f"{self._exe_s[tc]:.3f}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for ti in test_infos:
            self._exe_s[ti.case] = self._alpha * ti.result.time_s + (1.0 - self._alpha) * self._exe_s[ti.case]

    @override
    def reset(self) -> None:
        self._exe_s.clear()
