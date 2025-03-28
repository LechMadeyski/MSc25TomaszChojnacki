from typing import Protocol, Sequence
import numpy as np

type CodeVector = list[float] | np.ndarray


class CodeVectorizer(Protocol):
    def vectorize(self, code: str) -> CodeVector:
        raise NotImplementedError
