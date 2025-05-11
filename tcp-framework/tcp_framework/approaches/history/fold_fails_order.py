from collections import defaultdict
from math import inf
from random import Random
from typing import Callable, Literal, Optional, Sequence, override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach

type FailFolder = tuple[Literal["dfe"], float] | Literal["total", "recent"]


EPSILON = 1e-6


class FoldFailsOrder(Approach):
    """
    Original: https://doi.org/10.1109/ICSE.2002.1007961
    """

    def __init__(self, folder: FailFolder = ("dfe", 0.8), seed: Optional[int] = 0) -> None:
        initial, self._fold = self._select_folder(folder)
        self._fails: defaultdict[TestCase, float] = defaultdict(lambda: initial)
        self._seed = seed
        self._rng = Random(seed)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        if self._seed is not None:
            queue = ctx.test_cases.copy()
            while queue:
                weights = [self._fails[tc] for tc in queue]
                if sum(weights) < EPSILON:
                    weights = [1.0] * len(queue)
                [tc] = self._rng.choices(queue, weights)
                queue.remove(tc)
                ctx.execute(tc)
        else:
            for tc in sorted(ctx.test_cases, key=lambda tc: self._fails[tc], reverse=True):
                ctx.execute(tc, key=f"{self._fails[tc]:.3f}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for ti in test_infos:
            self._fails[ti.case] = self._fold(self._fails[ti.case], ti.result.fails)

    @override
    def reset(self) -> None:
        self._fails.clear()
        self._rng.seed(self._seed)

    @classmethod
    def _select_folder(cls, folder: FailFolder) -> tuple[float, Callable[[float, int], float]]:
        match folder:
            case ("dfe", alpha):
                assert isinstance(alpha, float)  # silence mypy
                return 0.0, lambda acc, value: alpha * abs(value) + (1.0 - alpha) * acc
            case "total":
                return 0.0, lambda acc, value: acc + value
            case "recent":
                return -inf, lambda acc, value: 0 if value > 0 else acc - 1
            case _:
                raise ValueError(f"unsupported folder: {folder}")
