from abc import ABC, abstractmethod
from ..datatypes import RunContext, TestCase, TestInfo


class Approach(ABC):
    @abstractmethod
    def prioritize(self, ctx: RunContext) -> None:
        raise NotImplementedError

    def get_dry_ordering(self, ctx: RunContext) -> list[TestCase]:
        forked_ctx = ctx.fork()
        self.prioritize(forked_ctx)
        return forked_ctx.prioritized_cases()

    def on_static_feedback(self, test_infos: list[TestInfo]) -> None:
        pass

    def reset(self) -> None:
        pass
