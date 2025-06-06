from collections.abc import Sequence
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach
from ..representation import CodeVectorizer, GroupAgg, LazyCodeDistMap, StVectorizer, VectorDist


class CodeDistBrokenOrder(Approach):
    """
    Proposed.
    """

    def __init__(
        self,
        target: Approach,
        vectorizer: CodeVectorizer = StVectorizer.default,
        distance: VectorDist = VectorDist.euclid,
        aggregation: GroupAgg = GroupAgg.min,
        *,
        switching: bool = True,
    ) -> None:
        self._target = target
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._switching = switching

    @override
    def prioritize(self, ctx: RunContext) -> None:
        distance = LazyCodeDistMap(ctx, self._vectorizer, self._distance)

        clusters = self._target.get_dry_ordering(ctx)

        prioritized: set[TestCase] = set()

        for cluster in clusters:

            def select(target: TestCase, cluster: list[TestCase] = cluster) -> None:
                cluster.remove(target)
                prioritized.add(target)
                ctx.execute(target)

            if len(cluster) == 1:
                select(cluster[0])
                continue

            if not prioritized:
                target = max(
                    cluster,
                    key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in cluster if tc1 != tc2),
                )
                select(target)

            optimum = min if self._switching and len(prioritized) < len(ctx.test_cases) * 0.5 else max

            while cluster:
                target = optimum(
                    cluster,
                    key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in prioritized),
                )
                select(target)

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._target.reset()
