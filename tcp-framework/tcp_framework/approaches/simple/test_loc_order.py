from typing import override
from ...datatypes import RunContext, TestCase
from ..approach import Approach


class TestLocOrder(Approach):
    """
    Proposed.
    """

    def __init__(self, skip_blank: bool = True) -> None:
        self._skip_blank = skip_blank

    @override
    def prioritize(self, ctx: RunContext) -> None:
        locs: dict[TestCase, int] = {}
        for case in ctx.test_cases:
            lines = ctx.inspect_code(case).strip().splitlines()
            if self._skip_blank:
                lines = [line for line in lines if len(line.strip()) > 0]
            locs[case] = len(lines)

        for case in sorted(ctx.test_cases, key=lambda tc: locs[tc], reverse=True):
            ctx.execute(case)
