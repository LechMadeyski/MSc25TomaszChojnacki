from random import Random
from typing import override
from ...datatypes import RunContext
from ..approach import Approach


class RandomOrder(Approach):
    """
    Original: https://doi.org/10.1109/ICSM.1999.792604
    """

    def __init__(self, seed: int = 0) -> None:
        self._seed = seed
        self._rng = Random(seed)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        cases = ctx.test_cases[:]
        self._rng.shuffle(cases)
        for tc in cases:
            ctx.execute(tc)

    @override
    def reset(self) -> None:
        self._rng.seed(self._seed)
