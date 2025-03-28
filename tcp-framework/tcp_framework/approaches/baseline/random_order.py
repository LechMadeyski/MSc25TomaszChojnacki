from random import Random
from ...datatypes import RunContext
from ..tcp_approach import TcpApproach


class RandomOrder(TcpApproach):
    def __init__(self, seed: int = 0) -> None:
        self._rng = Random(seed)

    def prioritize(self, ctx: RunContext) -> None:
        self._rng.shuffle(ctx.test_cases)
        for tc in ctx.test_cases:
            ctx.execute(tc)
