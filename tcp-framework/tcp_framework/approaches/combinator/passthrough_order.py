from typing import override
from ...datatypes import RunContext, TestInfo
from ..approach import Approach


class PassthroughOrder(Approach):
    def __init__(self, target: Approach) -> None:
        self._target = target

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for case in self._target.get_dry_static_ordering(ctx):
            ctx.execute(case)

    @override
    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        self._target.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._target.reset()
