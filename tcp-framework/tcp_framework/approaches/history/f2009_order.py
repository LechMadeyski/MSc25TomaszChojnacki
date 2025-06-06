from collections import defaultdict
from collections.abc import Sequence
from random import Random
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach

EPSILON = 1e-6


class F2009Order(Approach):
    """
    Original: https://doi.org/10.1007/978-3-642-02949-3_5
    """

    def __init__(self, *, alpha: float = 0.04, beta: float = 0.7, gamma: float = 0.7, seed: int = 0) -> None:
        assert alpha >= 0.0, "alpha must be non-negative"
        assert beta >= 0.0, "beta must be non-negative"
        assert gamma >= 0.0, "gamma must be non-negative"

        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        self._seed = seed

        self._rng = Random(seed)
        self._fc: defaultdict[TestCase, int] = defaultdict(int)
        self._ec: defaultdict[TestCase, int] = defaultdict(int)
        self._h: defaultdict[TestCase, int] = defaultdict(int)
        self._pr: defaultdict[TestCase, float] = defaultdict(float)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        priorities: dict[TestCase, float] = {}
        for tc in ctx.test_cases:
            hfde = self._fc[tc] / self._ec[tc] if self._ec[tc] > 0 else 0.0
            priorities[tc] = self._alpha * self._h[tc] + self._beta * self._pr[tc] + self._gamma * hfde

        queue = ctx.test_cases.copy()
        while queue:
            weights = [priorities[tc] for tc in queue]
            if sum(weights) < EPSILON:
                weights = [1.0] * len(queue)
            [tc] = self._rng.choices(queue, weights)
            queue.remove(tc)
            ctx.execute(tc)

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        seen: set[TestCase] = set()
        for ti in test_infos:
            tc = ti.case
            hfde = self._fc[tc] / self._ec[tc] if self._ec[tc] > 0 else 0.0
            self._pr[tc] = self._alpha * self._h[tc] + self._beta * self._pr[tc] + self._gamma * hfde
            self._fc[tc] += int(ti.result.fails > 0)
            self._ec[tc] += 1
            seen.add(tc)
        for tc in set(self._h.keys()) - seen:
            self._h[tc] += 1

    @override
    def reset(self) -> None:
        self._rng.seed(self._seed)
        self._fc.clear()
        self._ec.clear()
        self._h.clear()
        self._pr.clear()
