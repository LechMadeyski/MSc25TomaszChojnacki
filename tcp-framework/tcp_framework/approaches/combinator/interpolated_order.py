from random import Random
from typing import Literal, Sequence, override

from ...datatypes import RunContext, TestInfo
from ...deep import deep_any, deep_len, deep_remove
from ..approach import Approach

type Mode = Literal["all", "failed"]


class InterpolatedOrder(Approach):
    """
    Proposed. ?
    """

    def __init__(self, before: Approach, cutoff: int, after: Approach, *, mode: Mode = "all", seed: int = 0) -> None:
        assert cutoff >= 0, "cutoff must be an index"
        self._before = before
        self._cutoff = cutoff
        self._after = after
        self._mode = mode
        self._seed = seed
        self._rng = Random(seed)
        self._cycle = 0

    @override
    def prioritize(self, ctx: RunContext) -> None:
        if self._cycle >= self._cutoff:
            return self._after.prioritize(ctx)

        before = self._before.get_dry_ordering(ctx)
        after = self._after.get_dry_ordering(ctx)
        after_weight = self._cycle / self._cutoff

        for _ in range(deep_len(before)):
            real = self._rng.random()
            target_group = after[0] if real < after_weight else before[0]
            target = self._rng.choice(target_group)
            deep_remove(before, target)
            deep_remove(after, target)
            ctx.execute(target)

        match self._mode:
            case "all":
                self._cycle += 1
            case "failed":
                if deep_any(ctx.prioritized_infos(), lambda ti: ti.result.fails > 0):
                    self._cycle += 1

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        self._before.on_static_feedback(test_infos)
        self._after.on_static_feedback(test_infos)

    @override
    def reset(self) -> None:
        self._before.reset()
        self._after.reset()
        self._rng.seed(self._seed)
        self._cycle = 0
