from collections import defaultdict
from math import inf
from typing import Callable, Literal, override
from ..approach import Approach
from ...datatypes import RunContext, TestCase

type FailureFolder = tuple[Literal["dfe"], float] | Literal["total", "recent"]


class FoldFailuresOrder(Approach):
    def __init__(self, folder: FailureFolder = ("dfe", 0.8)) -> None:
        initial, self._fold = self._select_folder(folder)
        self._failures: defaultdict[TestCase, float] = defaultdict(lambda: initial)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._failures[tc], reverse=True):
            result = ctx.execute(tc)
            self._failures[tc] = self._fold(self._failures[tc], result.failures)

    @override
    def reset(self) -> None:
        self._failures.clear()

    @classmethod
    def _select_folder(cls, folder: FailureFolder) -> tuple[float, Callable[[float, int], float]]:
        match folder:
            case ("dfe", alpha):
                assert isinstance(alpha, float)  # silence mypy
                return 0.0, lambda acc, value: alpha * abs(value) + (1.0 - alpha) * acc
            case "total":
                return 0.0, lambda acc, value: acc + value
            case "recent":
                return -inf, lambda acc, value: 0 if value > 0 else acc - 1
            case _:
                raise ValueError
