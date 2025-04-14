from collections import defaultdict
from typing import DefaultDict, override
from itertools import groupby
from ...datatypes import RunContext, TestCase
from ..approach import Approach
from ..representation import GroupAgg, MinAgg, VectorDist, EuclidDist, CodeVectorizer, LazyCodeDistMap


class FailCodeDistOrder(Approach):
    def __init__(
        self,
        vectorizer: CodeVectorizer,
        distance: VectorDist = EuclidDist(),
        aggregation: GroupAgg = MinAgg(),
    ) -> None:
        self._total_fails: DefaultDict[str, int] = defaultdict(lambda: 0)
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation

    @override
    def prioritize(self, ctx: RunContext) -> None:
        distance = LazyCodeDistMap(ctx, self._vectorizer, self._distance)

        clusters = [
            set(g)
            for _, g in groupby(
                sorted(ctx.test_cases, key=lambda tc: self._total_fails[tc.name], reverse=True),
                key=lambda tc: self._total_fails[tc.name],
            )
        ]

        prioritized: set[TestCase] = set()

        for cluster in clusters:

            def select(target: TestCase) -> None:
                cluster.remove(target)
                result = ctx.execute(target)
                prioritized.add(target)
                self._total_fails[target.name] += result.fails

            if len(cluster) == 1:
                (target,) = cluster
                select(target)
                continue

            if not prioritized:
                target = max(
                    cluster,
                    key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in cluster if tc1 != tc2),
                )
                select(target)

            optimum = min if len(prioritized) < len(ctx.test_cases) * 0.5 else max

            while cluster:
                target = optimum(
                    cluster,
                    key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in prioritized),
                )
                select(target)

    @override
    def reset(self) -> None:
        self._total_fails.clear()
