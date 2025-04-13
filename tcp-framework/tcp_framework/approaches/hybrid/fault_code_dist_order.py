from collections import defaultdict
from typing import DefaultDict, override
from itertools import groupby
import numpy as np
from tqdm import tqdm
from ...datatypes import RunContext, TestCase
from ..approach import Approach
from ..representation.aggregations import GroupAgg, MinAgg
from ..representation.distances import VectorDist, EuclidDist
from ..representation.vectorizers import CodeVectorizer


class FaultCodeDistOrder(Approach):
    def __init__(
        self,
        vectorizer: CodeVectorizer,
        distance: VectorDist = EuclidDist(),
        aggregation: GroupAgg = MinAgg(),
        *,
        debug: bool = False,
    ) -> None:
        self._total_failures: DefaultDict[str, int] = defaultdict(lambda: 0)
        self._vectorizer = vectorizer
        self._distance = distance
        self._aggregation = aggregation
        self._debug = debug

    @override
    def prioritize(self, ctx: RunContext) -> None:
        embeddings: dict[TestCase, np.ndarray] = {}
        for tc in tqdm(ctx.test_cases, desc="Vectorizing", leave=False, disable=not self._debug):
            embeddings[tc] = self._vectorizer(ctx.inspect_code(tc))

        distances: dict[tuple[TestCase, TestCase], float] = {}
        for i, tc1 in enumerate(ctx.test_cases):
            for tc2 in ctx.test_cases[i + 1 :]:
                if tc1 != tc2:
                    distances[(tc1, tc2)] = self._distance(embeddings[tc1], embeddings[tc2])
                    distances[(tc2, tc1)] = distances[(tc1, tc2)]

        clusters = [
            set(g)
            for _, g in groupby(
                sorted(ctx.test_cases, key=lambda tc: self._total_failures[tc.name], reverse=True),
                key=lambda tc: self._total_failures[tc.name],
            )
        ]

        prioritized: set[TestCase] = set()

        for cluster in clusters:

            def select(target: TestCase) -> None:
                cluster.remove(target)
                result = ctx.execute(target)
                prioritized.add(target)
                self._total_failures[target.name] += result.failures

            if len(cluster) == 1:
                (target,) = cluster
                select(target)
                continue

            if not prioritized:
                target = max(
                    cluster,
                    key=lambda tc1: self._aggregation(distances[(tc1, tc2)] for tc2 in cluster if tc1 != tc2),
                )
                select(target)

            optimum = min if len(prioritized) < len(ctx.test_cases) * 0.5 else max

            while cluster:
                target = optimum(
                    cluster,
                    key=lambda tc1: self._aggregation(distances[(tc1, tc2)] for tc2 in prioritized),
                )
                select(target)

    @override
    def reset(self) -> None:
        self._total_failures.clear()
