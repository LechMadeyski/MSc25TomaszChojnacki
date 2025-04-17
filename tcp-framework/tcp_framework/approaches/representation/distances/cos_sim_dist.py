import numpy as np
from sentence_transformers.util import cos_sim
from .vector_dist import VectorDist


class CosSimDist(VectorDist):
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        return 1 - cos_sim(v1, v2)
