from collections import defaultdict
from typing import DefaultDict
from ..tcp_approach import TcpApproach
from ...datatypes import RunContext, TestCase


class DfeOrder(TcpApproach):
    def __init__(self, alpha: float = 0.8) -> None:
        self._alpha = alpha
        self._p: DefaultDict[TestCase, float] = defaultdict(lambda: 0)

    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._p[tc], reverse=True):
            result = ctx.execute(tc)
            f = 1 if result.failures > 0 else 0
            self._p[tc] = self._alpha * f + (1 - self._alpha) * self._p[tc]
