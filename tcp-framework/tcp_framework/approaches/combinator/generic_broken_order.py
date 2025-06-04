from collections.abc import Sequence
from typing import override

from ...datatypes import RunContext, TestInfo
from ..approach import Approach


class GenericBrokenOrder(Approach):
    """
    Proposed.
    """

    def __init__(self, *, target: Approach, breaker: Approach) -> None:
        self._target = target
        self._breaker = breaker

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for ci, cluster in enumerate(self._target.get_dry_ordering(ctx)):
            for ti, tcs in enumerate(self._breaker.get_dry_ordering(ctx.fork(cluster))):
                for tc in tcs:
                    ctx.execute(tc, key=f"{ci}:{ti}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._target.on_static_feedback(test_infos)
        self._breaker.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._target.reset()
        self._breaker.reset()
