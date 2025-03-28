from dataclasses import dataclass
from .test_case import TestCase
from .test_result import TestResult


@dataclass(frozen=True)
class TestInfo:
    name: str
    content: str
    failures: int
    duration_s: float

    def to_case(self) -> TestCase:
        return TestCase(name=self.name)

    def to_result(self) -> TestResult:
        return TestResult(failures=self.failures, duration_s=self.duration_s)
