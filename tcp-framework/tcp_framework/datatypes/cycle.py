from collections.abc import Sequence

from .test_info import TestInfo


class Cycle:
    def __init__(self, *, job_id: str, tests: Sequence[TestInfo], cycle_time_s: float | None) -> None:
        self.job_id = job_id
        self.tests = tests
        self.cycle_time_s = max(cycle_time_s or 0.0, self.execution_time_s)

    @property
    def is_failed(self) -> bool:
        return any(ti.result.fails > 0 for ti in self.tests)

    @property
    def execution_time_s(self) -> float:
        return sum(ti.result.time_s for ti in self.tests)

    @property
    def build_time_s(self) -> float:
        return self.cycle_time_s - self.execution_time_s
