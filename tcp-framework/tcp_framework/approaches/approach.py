from abc import ABC, abstractmethod
from typing import Callable, Sequence
from ..datatypes import RunContext, TestCase, TestInfo


class Approach(ABC):
    @abstractmethod
    def prioritize(self, ctx: RunContext) -> None: ...

    def get_dry_ordering(self, ctx: RunContext) -> list[TestCase]:
        forked_ctx = ctx.fork()
        self.prioritize(forked_ctx)
        return forked_ctx.prioritized_cases()

    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        pass

    def reset(self) -> None:
        pass


type ApproachFactory = Callable[[int], Approach]
