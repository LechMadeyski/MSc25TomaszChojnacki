from collections import Counter
from collections.abc import Sequence
from typing import override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach


class RecentnessOrder(Approach):
    def __init__(self, *, latest_only: bool = False) -> None:
        self._seen: Counter[TestCase] = Counter()
        self._latest_only = latest_only

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in sorted(ctx.test_cases, key=lambda tc: self._seen.get(tc, 0)):
            key = str(self._seen[tc] == min(self._seen.values(), default=0) if self._latest_only else self._seen[tc])
            ctx.execute(tc, key=str(key))

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._seen.update([ti.case for ti in test_infos])

    @override
    def reset(self) -> None:
        self._seen.clear()
