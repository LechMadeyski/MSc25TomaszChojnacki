from typing import override
from ...datatypes import RunContext
from ..approach import Approach
from .lazy_code_dist_map import LazyCodeDistMap
from .aggregations import GroupAgg
from .distances import VectorDist
from .vectorizers import CodeVectorizer


class CodeDistOrder(Approach):
    """
    Proposed.
    Similar: https://doi.org/10.1007/s10515-011-0093-0
    """

    def __init__(
        self,
        vectorizer: CodeVectorizer,
        distance: VectorDist,
        aggregation: GroupAgg,
        fail_adapt: int = 0,
    ) -> None:
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._fail_adapt = fail_adapt

    @override
    def prioritize(self, ctx: RunContext) -> None:
        distance = LazyCodeDistMap(ctx, self._vectorizer, self._distance)

        start = max(
            ctx.test_cases,
            key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in ctx.test_cases if tc1 != tc2),
        )
        prioritized = set([start])
        queue = ctx.test_cases.copy()
        queue.remove(start)
        local_searches = self._fail_adapt if (self._fail_adapt > 0 and ctx.execute(start).fails > 0) else 0

        while queue:
            optimum = min if local_searches > 0 else max
            found = optimum(
                queue,
                key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in prioritized),
            )
            prioritized.add(found)
            queue.remove(found)
            local_searches = (
                self._fail_adapt
                if (self._fail_adapt > 0 and ctx.execute(found).fails > 0)
                else max(local_searches - 1, 0)
            )
