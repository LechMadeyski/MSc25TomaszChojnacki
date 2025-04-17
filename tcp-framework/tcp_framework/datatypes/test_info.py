from .test_case import TestCase
from .test_result import TestResult


class TestInfo:
    def __init__(self, *, case: TestCase, content: str, result: TestResult):
        self.case = case
        self.content = content
        self.result = result
