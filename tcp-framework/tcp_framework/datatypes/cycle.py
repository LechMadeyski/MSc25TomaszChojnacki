from .test_info import TestInfo


class Cycle:
    def __init__(self, *, job_id: str, tests: list[TestInfo]) -> None:
        self.job_id = job_id
        self.tests = tests
