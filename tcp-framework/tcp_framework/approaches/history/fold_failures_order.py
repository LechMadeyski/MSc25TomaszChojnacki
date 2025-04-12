from collections import defaultdict
from typing import DefaultDict, Literal, override
from ..approach import Approach
from ...datatypes import RunContext, TestCase


def _dfe(failures: list[int]) -> float:
    p = 0.0
    for f in failures:
        if f > 1:
            f = 1
        p = 0.8 * f + 0.2 * p
    return p


def _total(failures: list[int]) -> float:
    return sum(failures)


def _last(failures: list[int]) -> float:
    return failures[-1] if len(failures) > 0 else 0


def _recent(failures: list[int]) -> float:
    for i in range(len(failures)):
        if failures[len(failures) - i - 1] > 0:
            return -i
    return -float("inf")


class FoldFailuresOrder(Approach):
    def __init__(
        self,
        func: Literal["dfe"] | Literal["total"] | Literal["last"] | Literal["recent"],
    ) -> None:
        self._failures: DefaultDict[TestCase, list[int]] = defaultdict(lambda: [])
        match func:
            case "dfe":
                self._func = _dfe
            case "total":
                self._func = _total
            case "last":
                self._func = _last
            case "recent":
                self._func = _recent
            case _:
                raise ValueError

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._func(self._failures[tc]), reverse=True):
            result = ctx.execute(tc)
            self._failures[tc].append(result.failures)

    @override
    def reset(self) -> None:
        self._failures.clear()
