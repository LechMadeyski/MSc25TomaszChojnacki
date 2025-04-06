from random import Random
from typing import override
from ...datatypes import RunContext
from ..approach import Approach


class RandomOrder(Approach):
    def __init__(self, seed: int = 0) -> None:
        self._seed = seed
        self._rng = Random(seed)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        self._rng.shuffle(ctx.test_cases)
        for tc in ctx.test_cases:
            ctx.execute(tc)

    @override
    def reset(self) -> None:
        self._rng.seed(self._seed)
