from typing import Callable, override

from ...datatypes import RunContext, TestCase
from ..approach import Approach
from .utils import GroupAgg, lccss, normalize_code


class SimilarityOrder(Approach):
    """
    Proposed.
    Similar: https://doi.org/10.1007/s10515-011-0093-0
    """

    def __init__(self, similarity: Callable[[str, str], int] = lccss, aggregation: GroupAgg = GroupAgg.min) -> None:
        self._similarity = similarity
        self._aggregation = aggregation

    @override
    def prioritize(self, ctx: RunContext) -> None:
        if len(ctx.test_cases) <= 1:
            if len(ctx.test_cases) == 1:
                ctx.execute(ctx.test_cases[0])
            return

        codes = {tc: normalize_code(ctx.inspect_code(tc)) for tc in ctx.test_cases}
        prioritized: set[TestCase] = set()
        queue = ctx.test_cases.copy()

        def select(tc: TestCase) -> None:
            ctx.execute(tc)
            prioritized.add(tc)
            queue.remove(tc)

        start = max(
            ctx.test_cases,
            key=lambda tc1: self._aggregation(
                -self._similarity(codes[tc1], codes[tc2]) for tc2 in ctx.test_cases if tc1 != tc2
            ),
        )
        select(start)

        while queue:
            found = max(
                queue,
                key=lambda tc1: self._aggregation(-self._similarity(codes[tc1], codes[tc2]) for tc2 in prioritized),
            )
            select(found)
