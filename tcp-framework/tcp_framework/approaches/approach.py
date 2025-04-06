from abc import ABC, abstractmethod
from ..datatypes import RunContext


class Approach(ABC):
    @abstractmethod
    def prioritize(self, ctx: RunContext) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        pass
