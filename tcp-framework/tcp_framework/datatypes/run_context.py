from collections.abc import Sequence
from typing import override

from ..deep import deep_len, deep_map, flatten
from .test_case import Ordering, TestCase
from .test_info import TestInfo
from .test_result import TestResult


class RunContext:
    def __init__(self, test_infos: Sequence[TestInfo]) -> None:
        self._test_infos = {ti.case: ti for ti in test_infos}
        self._executed: Ordering = []
        self._last_key: str | None = None

    @property
    def test_cases(self) -> list[TestCase]:
        return list(self._test_infos.keys())

    def execute(self, test_case: TestCase, *, key: str | None = None) -> TestResult:
        if test_case in flatten(self._executed) or test_case not in self._test_infos:
            raise ValueError("test case was already executed or does not belong to this context")
        if key is not None and key == self._last_key:
            self._executed[-1].append(test_case)
        else:
            self._executed.append([test_case])
        self._last_key = key
        return self._test_infos[test_case].result

    def inspect_code(self, test_case: TestCase) -> str:
        return self._test_infos[test_case].content

    def prioritized_cases(self) -> Ordering:
        if deep_len(self._executed) != len(self._test_infos):
            raise ValueError("not all test cases were executed")
        return self._executed

    def prioritized_infos(self) -> Ordering[TestInfo]:
        if deep_len(self._executed) != len(self._test_infos):
            raise ValueError("not all test cases were executed")
        return deep_map(self._executed, lambda tc: self._test_infos[tc])

    def fork(self, test_cases: Sequence[TestCase] | None = None) -> "ForkedRunContext":
        test_infos = list(self._test_infos.values())
        if test_cases is not None:
            test_infos = [ti for tc, ti in self._test_infos.items() if tc in test_cases]
        return ForkedRunContext(test_infos)


class ForkedRunContext(RunContext):
    @override
    def execute(self, test_case: TestCase, *, key: str | None = None) -> TestResult:
        return super().execute(test_case, key=key).hide()  # only leak results in the top RunContext

    @override
    def prioritized_infos(self) -> Ordering[TestInfo]:
        raise ValueError  # only leak results in the top RunContext
