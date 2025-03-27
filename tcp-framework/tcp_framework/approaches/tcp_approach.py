from typing import Protocol
from ..datatypes import RunContext


class TcpApproach(Protocol):
    def prioritize(self, ctx: RunContext) -> None:
        pass
