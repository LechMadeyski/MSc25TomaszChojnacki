import numpy as np
from sentence_transformers.util import cos_sim
from ...datatypes import RunContext, TestCase
from ..tcp_approach import TcpApproach
from .aggregations import GroupAgg
from .distances import VectorDist
from .vectorizers import CodeVectorizer


class Proposed(TcpApproach):
    def __init__(
        self, vectorizer: CodeVectorizer, distance: VectorDist, aggregation: GroupAgg
    ) -> None:
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation

    def prioritize(self, ctx: RunContext) -> None:
        embeddings: dict[TestCase, np.ndarray] = {}
        for tc in ctx.test_cases:
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
        ctx.execute(start)

        while queue:
            found = max(
                queue,
                key=lambda tc1: self._aggregation(
                    self._distance(embeddings[tc1], embeddings[tc2])
                    for tc2 in prioritized
                ),
            )
            prioritized.add(found)
            queue.remove(found)
            ctx.execute(found)
