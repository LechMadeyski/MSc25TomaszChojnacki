from collections import defaultdict
from itertools import groupby
from typing import Callable, Sequence, override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach
from ..representation import GroupAgg, lccss
from ..representation.utils import normalize_code


class FailSimilarityOrder(Approach):
    """
    Proposed.
    """

    def __init__(
        self,
        similarity: Callable[[str, str], int] = lccss,
        aggregation: GroupAgg = GroupAgg.min,
    ) -> None:
        self._total_fails: defaultdict[TestCase, int] = defaultdict(lambda: 0)
        self._similarity = similarity
        self._aggregation = aggregation

    @override
    def prioritize(self, ctx: RunContext) -> None:
        clusters = [
            set(g)
            for _, g in groupby(
                sorted(ctx.test_cases, key=lambda tc: self._total_fails[tc], reverse=True),
                key=lambda tc: self._total_fails[tc],
            )
        ]

        codes = {tc: normalize_code(ctx.inspect_code(tc)) for tc in ctx.test_cases}
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
        for ti in test_infos:
            self._total_fails[ti.case] += ti.result.fails

    @override
    def reset(self) -> None:
        self._total_fails.clear()
