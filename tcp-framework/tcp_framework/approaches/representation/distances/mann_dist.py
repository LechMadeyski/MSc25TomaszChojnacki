import numpy as np
from .vector_dist import VectorDist


class MannDist(VectorDist):
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        return np.sum(np.abs(v1 - v2))
