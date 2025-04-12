from typing import override
import numpy as np
from tqdm import tqdm
from ...datatypes import RunContext, TestCase
from ..approach import Approach
from .aggregations import GroupAgg
from .distances import VectorDist
from .vectorizers import CodeVectorizer


class CodeDistOrder(Approach):
    def __init__(
        self,
        vectorizer: CodeVectorizer,
        distance: VectorDist,
        aggregation: GroupAgg,
        fail_adapt: int = 0,
        *,
        debug: bool = False,
    ) -> None:
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._fail_adapt = fail_adapt
        self._debug = debug

    @override
    def prioritize(self, ctx: RunContext) -> None:
        if len(ctx.test_cases) <= 1:
            if len(ctx.test_cases) == 1:
                ctx.execute(ctx.test_cases[0])
            return

        embeddings: dict[TestCase, np.ndarray] = {}
        for tc in tqdm(ctx.test_cases, desc="Vectorizing", leave=False, disable=not self._debug):
            embeddings[tc] = self._vectorizer(ctx.inspect_code(tc))

        distances: dict[tuple[TestCase, TestCase], float] = {}
        for i, tc1 in enumerate(ctx.test_cases):
            for tc2 in ctx.test_cases[i + 1 :]:
                if tc1 != tc2:
                    distances[(tc1, tc2)] = self._distance(embeddings[tc1], embeddings[tc2])
                    distances[(tc2, tc1)] = distances[(tc1, tc2)]

        start = max(
            ctx.test_cases,
            key=lambda tc1: self._aggregation(distances[(tc1, tc2)] for tc2 in ctx.test_cases if tc1 != tc2),
        )
        prioritized = set([start])
        queue = ctx.test_cases.copy()
        queue.remove(start)
        local_searches = self._fail_adapt if ctx.execute(start).failures > 0 else 0

        while queue:
            optimum = min if local_searches > 0 else max
            found = optimum(
                queue,
                key=lambda tc1: self._aggregation(distances[(tc1, tc2)] for tc2 in prioritized),
            )
            prioritized.add(found)
            queue.remove(found)
            local_searches = self._fail_adapt if ctx.execute(found).failures > 0 else local_searches - 1
