import numpy as np
from typing import Protocol


class VectorDist(Protocol):
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        raise NotImplementedError
