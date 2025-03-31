import numpy as np
from tqdm import tqdm
from ...datatypes import RunContext, TestCase
from ..tcp_approach import TcpApproach
from .aggregations import GroupAgg
from .distances import VectorDist
from .vectorizers import CodeVectorizer


class CodeDistOrder(TcpApproach):
    def __init__(
        self,
        vectorizer: CodeVectorizer,
        distance: VectorDist,
        aggregation: GroupAgg,
        fail_adapt: bool = False,
        *,
        debug: bool = False,
    ) -> None:
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._fail_adapt = fail_adapt
        self._debug = debug

    def prioritize(self, ctx: RunContext) -> None:
        embeddings: dict[TestCase, np.ndarray] = {}
        for tc in tqdm(ctx.test_cases, desc="Vectorizing", leave=False, disable=not self._debug):
            embeddings[tc] = self._vectorizer(ctx.inspect_code(tc))

        start = max(
            ctx.test_cases,
            key=lambda tc1: self._aggregation(
                self._distance(embeddings[tc1], embeddings[tc2])
                for tc2 in ctx.test_cases
                if tc1 != tc2
            ),
        )
        prioritized = set([start])
        queue = ctx.test_cases.copy()
        queue.remove(start)
        last_result = ctx.execute(start)

        while queue:
            optimum = min if self._fail_adapt and last_result.failures > 0 else max
            found = optimum(
                queue,
                key=lambda tc1: self._aggregation(
                    self._distance(embeddings[tc1], embeddings[tc2])
                    for tc2 in prioritized
                ),
            )
            prioritized.add(found)
            queue.remove(found)
            last_result = ctx.execute(found)
