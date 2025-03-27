from ..datatypes import RunContext
from .tcp_approach import TcpApproach


class BaseOrder(TcpApproach):
    def prioritize(self, ctx: RunContext) -> None:
        for tc in ctx.test_cases:
            ctx.execute(tc)
