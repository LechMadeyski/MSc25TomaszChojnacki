from typing import override
from ...datatypes import RunContext
from ..approach import Approach


class BaseOrder(Approach):
    """
    Original: https://doi.org/10.1109/ICSM.1999.792604
    """

    @override
    def prioritize(self, ctx: RunContext) -> None:
        for tc in ctx.test_cases:
            ctx.execute(tc)
