from collections import defaultdict
from functools import cmp_to_key
from itertools import product
from typing import override

from ...datatypes import Ordering, TestCase
from ...deep import flatten
from .mixed_order import MixedOrder

EPSILON = 1e-6


class SchulzeMixedOrder(MixedOrder):
    """
    Proposed.
    Similar: https://doi.org/10.18293/SEKE2022-148
    Similar: https://doi.org/10.1109/TR.2022.3205483
    """

    @override
    def merge_queues(self, queues: list[Ordering]) -> Ordering:
        d: defaultdict[tuple[TestCase, TestCase], float] = defaultdict(float)
        for qi, queue in enumerate(queues):
            weight = self._weights[qi]
            for i, higher in enumerate(queue):
                for lower in queue[i + 1 :]:
                    for hi in higher:
                        for lo in lower:
                            d[(hi, lo)] += weight

        unique_cases = set(flatten(queues[0]))
        p: defaultdict[tuple[TestCase, TestCase], float] = defaultdict(float)
        for tc1, tc2 in product(unique_cases, repeat=2):
            if tc1 != tc2:
                p[(tc1, tc2)] = d[(tc1, tc2)] if d[(tc1, tc2)] > d[(tc2, tc1)] else 0
        for tc1, tc2, tc3 in product(unique_cases, repeat=3):
            if len({tc1, tc2, tc3}) == 3:
                p[(tc2, tc3)] = max(p[(tc2, tc3)], min(p[(tc2, tc1)], p[(tc1, tc3)]))

        def cmp(tc1: TestCase, tc2: TestCase) -> int:
            delta = p[(tc2, tc1)] - p[(tc1, tc2)]
            if delta > EPSILON:
                return 1
            if delta < -EPSILON:
                return -1
            return 0

        tcs = sorted(unique_cases, key=cmp_to_key(cmp))
        result: Ordering = []
        while tcs:
            tc = tcs.pop(0)
            group = [tc]
            for other in tcs:
                if abs(p[(tc, other)] - p[(other, tc)]) < EPSILON:
                    group.append(other)
                    tcs.remove(other)
            result.append(group)
        return result
