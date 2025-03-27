from dataclasses import dataclass
from collections.abc import Callable
from .test_case import TestCase
from .test_result import TestResult


@dataclass(frozen=True)
class RunContext:
    test_cases: list[TestCase]
    execute: Callable[[TestCase], TestResult]
    inspect_code: Callable[[TestCase], str]
