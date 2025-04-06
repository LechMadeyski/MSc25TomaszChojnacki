from typing import override
from ...datatypes import RunContext
from ..approach import Approach


class BaseOrder(Approach):
    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in ctx.test_cases:
            ctx.execute(tc)
