from collections import Counter
from typing import Sequence, override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach


class RecentnessOrder(Approach):
    def __init__(self) -> None:
        self._seen: Counter[TestCase] = Counter()

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._seen.get(tc, 0)):
            ctx.execute(tc, key=str(self._seen[tc]))

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._seen.update([ti.case for ti in test_infos])

    @override
    def reset(self) -> None:
        self._seen.clear()
