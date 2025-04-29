from typing import Sequence, override

from .test_case import TestCase
from .test_info import TestInfo
from .test_result import TestResult


class RunContext:
    def __init__(self, test_infos: Sequence[TestInfo]) -> None:
        self._test_infos = {ti.case: ti for ti in test_infos}
        self._executed: list[TestCase] = []

    @property
    def test_cases(self) -> list[TestCase]:
        return list(self._test_infos.keys())

    def execute(self, test_case: TestCase) -> TestResult:
        if test_case in self._executed or test_case not in self._test_infos:
            raise ValueError("test case was already executed or does not belong to this context")
        self._executed.append(test_case)
        return self._test_infos[test_case].result

    def inspect_code(self, test_case: TestCase) -> str:
        return self._test_infos[test_case].content

    def prioritized_cases(self) -> list[TestCase]:
        if len(self._executed) != len(self._test_infos):
            raise ValueError("not all test cases were executed")
        return self._executed

    def prioritized_infos(self) -> list[TestInfo]:
        if len(self._executed) != len(self._test_infos):
            raise ValueError("not all test cases were executed")
        return [self._test_infos[tc] for tc in self._executed]

    def fork(self) -> "ForkedRunContext":
        return ForkedRunContext(list(self._test_infos.values()))


class ForkedRunContext(RunContext):
    @override
    def execute(self, test_case: TestCase) -> TestResult:
        return super().execute(test_case).hide()  # only leak results in the top RunContext

    @override
    def prioritized_infos(self) -> list[TestInfo]:
        raise ValueError  # only leak results in the top RunContext
