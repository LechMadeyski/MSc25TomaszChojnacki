import numpy as np
from .vector_dist import VectorDist
from ..vectorizers import CodeVectorizer
from ....datatypes import TestCase, RunContext


class LazyCodeDistMap:
    def __init__(self, ctx: RunContext, vectorizer: CodeVectorizer, distance: VectorDist) -> None:
        self._ctx = ctx
        self._calc_vector = vectorizer
        self._calc_dist = distance

        self._vector_map: dict[TestCase, np.ndarray] = {}
        self._dist_map: dict[tuple[TestCase, TestCase], float] = {}

    def __call__(self, tc1: TestCase, tc2: TestCase) -> float:
        if (value := self._dist_map.get((tc1, tc2))) is not None:
            return value
        result = self._calc_dist(self._get_or_calc_vector(tc1), self._get_or_calc_vector(tc2))
        self._dist_map[(tc1, tc2)] = result
        self._dist_map[(tc2, tc1)] = result
        return result

    def _get_or_calc_vector(self, tc: TestCase) -> np.ndarray:
        if (value := self._vector_map.get(tc)) is not None:
            return value
        result = self._calc_vector(self._ctx.inspect_code(tc))
        self._vector_map[tc] = result
        return result
