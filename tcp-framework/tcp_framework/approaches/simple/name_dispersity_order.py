from random import Random
from typing import override

from ...datatypes import RunContext
from ..approach import Approach


class NameDispersityOrder(Approach):
    """
    Original: https://doi.org/10.1109/TR.2020.2979815
    """

    def __init__(self, *, memory: int = 10, candidates: int = 10, alphabetic: bool = False, seed: int = 0) -> None:
        self._memory = memory
        self._candidates = candidates
        self._alphabetic = alphabetic
        self._seed = seed
        self._rng = Random(seed)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        cases = sorted(ctx.test_cases, key=lambda tc: tc.name) if self._alphabetic else ctx.test_cases
        n = len(cases)
        a = list(range(n))  # 1.
        m = self._rng.randint(0, n - 1)  # 2.
        a[0], a[m] = a[m], a[0]  # 3.
        selected = 1  # 4.
        while selected < n - 1:  # 5.
            memory = min(selected, self._memory)  # 6.
            candidates = self._rng.sample(list(range(selected, n)), min(self._candidates, n - selected))  # 7.
            d = {ci: min(abs(a[ci] - a[selected - i]) for i in range(1, memory + 1)) for ci in candidates}  # 7.
            r = max(candidates, key=lambda ci: d[ci])  # 7.
            a[selected], a[r] = a[r], a[selected]  # 8.
            selected += 1  # 9.
        for i in a:
            ctx.execute(cases[i])

    @override
    def reset(self) -> None:
        self._rng.seed(self._seed)
