from collections import defaultdict
from typing import override

from ...datatypes import Ordering, TestCase
from ...deep import deep_len
from .mixed_order import MixedOrder

EPSILON = 1e-6


class BordaMixedOrder(MixedOrder):
    """
    Proposed.
    Similar: https://doi.org/10.18293/SEKE2022-148
    Similar: https://doi.org/10.1109/TR.2022.3205483
    """

    @override
    def merge_queues(self, queues: list[Ordering]) -> Ordering:
        borda: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)
        for qi, queue in enumerate(queues):
            ti = 0
            size = deep_len(queue)
            for tcs in queue:
                max_score = size - ti - 1
                min_score = size - ti - len(tcs)
                votes = self._weights[qi] * (max_score + min_score) / 2
                for tc in tcs:
                    borda[tc] += votes
                ti += len(tcs)

        tcs = sorted(borda.keys(), key=lambda tc: borda[tc], reverse=True)
        result: Ordering = []
        last_score: float | None = None
        for tc in tcs:
            if last_score is None or abs(last_score - borda[tc]) > EPSILON:
                result.append([tc])
            else:
                result[-1].append(tc)
            last_score = borda[tc]
        return result
