from collections.abc import Sequence
from typing import Literal, override

from ...datatypes import RunContext, TestInfo
from ..approach import Approach
from .borda_mixed_order import BordaMixedOrder

type Mode = Literal["all", "failed"]


class InterpolatedOrder(Approach):
    """
    Proposed.
    """

    def __init__(self, before: Approach, cutoff: float, after: Approach, *, mode: Mode = "all") -> None:
        assert cutoff >= 0, "cutoff must be non-negative"
        self._before = before
        self._cutoff = cutoff
        self._after = after
        self._mode = mode
        self._cycle = 0

    @override
    def prioritize(self, ctx: RunContext) -> None:
        if self._cycle >= self._cutoff:
            self._after.prioritize(ctx)
            return

        after_weight = self._cycle / self._cutoff
        mixer = BordaMixedOrder([self._before, self._after], weights=[1.0 - after_weight, after_weight])
        mixer.prioritize(ctx)

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._before.on_static_feedback(test_infos)
        self._after.on_static_feedback(test_infos)

        match self._mode:
            case "all":
                self._cycle += 1
            case "failed":
                if any(ti.result.fails > 0 for ti in test_infos):
                    self._cycle += 1

    @override
    def reset(self) -> None:
        self._before.reset()
        self._after.reset()
        self._cycle = 0
