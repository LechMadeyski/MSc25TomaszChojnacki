import numpy as np
from .vector_dist import VectorDist


class EuclidDist(VectorDist):
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        return float(np.linalg.norm(v1 - v2))
