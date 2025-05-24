from collections.abc import Callable, Sequence
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach
from ..representation import GroupAgg, lccss
from ..representation.utils import normalize_code


class SimilarityBreakedOrder(Approach):
    """
    Proposed.
    """

    def __init__(
        self,
        target: Approach,
        similarity: Callable[[str, str], int] = lccss,
        aggregation: GroupAgg = GroupAgg.min,
    ) -> None:
        self._target = target
        self._similarity = similarity
        self._aggregation = aggregation

    @override
    def prioritize(self, ctx: RunContext) -> None:
        clusters = self._target.get_dry_ordering(ctx)

        codes = {tc: normalize_code(ctx.inspect_code(tc)) for tc in ctx.test_cases}
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
                    key=lambda tc1: self._aggregation(
                        -self._similarity(codes[tc1], codes[tc2]) for tc2 in cluster if tc1 != tc2
                    ),
                )
                select(target)

            optimum = min if len(prioritized) < len(ctx.test_cases) * 0.5 else max

            while cluster:
                target = optimum(
                    cluster,
                    key=lambda tc1: self._aggregation(-self._similarity(codes[tc1], codes[tc2]) for tc2 in prioritized),
                )
                select(target)

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._target.reset()
