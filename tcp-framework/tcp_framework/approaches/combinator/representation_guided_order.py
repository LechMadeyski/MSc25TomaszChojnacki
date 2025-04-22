from typing import override
from ...datatypes import RunContext, TestInfo
from ..representation import LazyCodeDistMap, CodeVectorizer, GroupAgg, MinAgg, VectorDist, EuclidDist
from ..approach import Approach


class RepresentationGuidedOrder(Approach):
    def __init__(
        self,
        target: Approach,
        vectorizer: CodeVectorizer,
        distance: VectorDist = EuclidDist(),
        aggregation: GroupAgg = MinAgg(),
        count: int = 2,
    ) -> None:
        self._target = target
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._count = count

    @override
    def prioritize(self, ctx: RunContext) -> None:
        queue = self._target.get_dry_static_ordering(ctx)
        distance = LazyCodeDistMap(ctx, self._vectorizer, self._distance)
        tc = queue.pop(0)
        ready = {tc}
        ctx.execute(tc)
        while queue:
            optimum = min if len(ready) < len(ctx.test_cases) * 0.5 else max
            target = optimum(
                queue[: self._count],
                key=lambda tc1: self._aggregation(distance(tc1, tc2) for tc2 in ready),
            )
            queue.remove(target)
            ready.add(target)
            ctx.execute(target)

    @override
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        self._target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._target.reset()
