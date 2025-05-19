from dataclasses import dataclass


@dataclass(frozen=True)
class TestCase:
    name: str


type Ordering[T = TestCase] = list[list[T]]
