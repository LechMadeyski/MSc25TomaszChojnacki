from abc import ABC, abstractmethod
from typing import override


class TestResult(ABC):
    @property
    @abstractmethod
    def fails(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def time_s(self) -> float:
        raise NotImplementedError

    def hide(self) -> "HiddenTestResult":
        return HiddenTestResult()


class VisibleTestResult(TestResult):
    def __init__(self, *, fails: int, time_s: float) -> None:
        self._fails = fails
        self._time_s = time_s

    @override
    @property
    def fails(self) -> int:
        return self._fails

    @override
    @property
    def time_s(self) -> float:
        return self._time_s


class HiddenTestResult(TestResult):
    @override
    @property
    def fails(self) -> int:
        raise ValueError

    @override
    @property
    def time_s(self) -> float:
        raise ValueError
