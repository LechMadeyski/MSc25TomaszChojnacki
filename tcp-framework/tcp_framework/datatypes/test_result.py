from dataclasses import dataclass


@dataclass(frozen=True)
class TestResult:
    failures: int
    duration_s: float
