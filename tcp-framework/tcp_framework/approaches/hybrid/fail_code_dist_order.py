from collections import defaultdict
from typing import DefaultDict, override
from itertools import groupby
from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach
from ..representation import GroupAgg, MinAgg, VectorDist, EuclidDist, CodeVectorizer, LazyCodeDistMap


class FailCodeDistOrder(Approach):
    """
    Proposed.
    """

    def __init__(
        self,
        vectorizer: CodeVectorizer,
        distance: VectorDist = EuclidDist(),
        aggregation: GroupAgg = MinAgg(),
    ) -> None:
        self._total_fails: DefaultDict[TestCase, int] = defaultdict(lambda: 0)
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation

    @override
    def prioritize(self, ctx: RunContext) -> None:
        distance = LazyCodeDistMap(ctx, self._vectorizer, self._distance)

        clusters = [
            set(g)
            for _, g in groupby(
                sorted(ctx.test_cases, key=lambda tc: self._total_fails[tc], reverse=True),
                key=lambda tc: self._total_fails[tc],
            )
        ]

        prioritized: set[TestCase] = set()

        for cluster in clusters:

            def select(target: TestCase) -> None:
                cluster.remove(target)
                prioritized.add(target)
                ctx.execute(target)

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
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        for ti in test_infos:
            self._total_fails[ti.case] += ti.result.fails

    @override
    def reset(self) -> None:
        self._total_fails.clear()
