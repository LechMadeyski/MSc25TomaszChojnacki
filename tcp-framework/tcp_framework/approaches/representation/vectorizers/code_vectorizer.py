from typing import Protocol

import numpy as np


class CodeVectorizer(Protocol):
    def __call__(self, code: str) -> np.ndarray: ...
