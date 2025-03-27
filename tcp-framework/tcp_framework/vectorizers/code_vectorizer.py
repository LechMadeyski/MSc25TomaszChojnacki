from typing import Protocol, Sequence


class CodeVectorizer(Protocol):
    def vectorize(self, code: str) -> Sequence[float]:
        pass
