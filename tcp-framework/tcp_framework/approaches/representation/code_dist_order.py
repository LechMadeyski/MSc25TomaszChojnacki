from typing import override

from ...datatypes import RunContext
from ..approach import Approach
from .utils import GroupAgg, LazyCodeDistMap, VectorDist
from .vectorizers import CodeVectorizer, StVectorizer


class CodeDistOrder(Approach):
    """
    Proposed.
    Similar: https://doi.org/10.1007/s10515-011-0093-0
    """

    def __init__(
        self,
        vectorizer: CodeVectorizer = StVectorizer.default,
        distance: VectorDist = VectorDist.euclid,
        aggregation: GroupAgg = GroupAgg.min,
        fail_adapt: int = 0,
    ) -> None:
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._fail_adapt = fail_adapt

    @override
    def prioritize(self, ctx: RunContext) -> None:
        if len(ctx.test_cases) <= 1:
            if len(ctx.test_cases) == 1:
                ctx.execute(ctx.test_cases[0])
            return

        distance = LazyCodeDistMap(ctx, self._vectorizer, self._distance)

        start = max(
            ctx.test_cases,
            key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in ctx.test_cases if tc1 != tc2),
        )
        prioritized = {start}
        queue = ctx.test_cases.copy()
        queue.remove(start)
        result = ctx.execute(start)
        local_searches = self._fail_adapt if (self._fail_adapt > 0 and result.fails > 0) else 0

        while queue:
            optimum = min if local_searches > 0 else max
            found = optimum(
                queue,
                key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in prioritized),
            )
            prioritized.add(found)
            queue.remove(found)
            result = ctx.execute(found)
            local_searches = (
                self._fail_adapt if (self._fail_adapt > 0 and result.fails > 0) else max(local_searches - 1, 0)
            )
