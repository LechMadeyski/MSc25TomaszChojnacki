from collections import defaultdict
from typing import override
from ...datatypes import TestCase
from .mixed_order import MixedOrder


class BordaMixedOrder(MixedOrder):
    """
    Proposed.
    Similar: https://doi.org/10.18293/SEKE2022-148
    Similar: https://doi.org/10.1109/TR.2022.3205483
    """

    @override
    def merge_queues(self, queues: list[list[TestCase]]) -> list[TestCase]:
        borda: defaultdict[TestCase, float] = defaultdict(lambda: 0.0)
        for qi, queue in enumerate(queues):
            for ti, tc in enumerate(queue):
                borda[tc] += (len(queue) - ti - 1) * self._weights[qi]
        return sorted(borda.keys(), key=lambda tc: borda[tc], reverse=True)
