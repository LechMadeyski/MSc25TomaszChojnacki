from abc import ABC, abstractmethod
from typing import override
from sentence_transformers.util import cos_sim
import numpy as np


class VectorDist(ABC):
    cos_sim: "VectorDist"
    euclid: "VectorDist"
    mann: "VectorDist"

    @abstractmethod
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float: ...


class _CosSimDist(VectorDist):
    @override
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        return 1 - cos_sim(v1, v2)


class _EuclidDist(VectorDist):
    @override
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        return float(np.linalg.norm(v1 - v2))


class _MannDist(VectorDist):
    @override
    def __call__(self, v1: np.ndarray, v2: np.ndarray) -> float:
        return np.sum(np.abs(v1 - v2))


VectorDist.cos_sim = _CosSimDist()
VectorDist.euclid = _EuclidDist()
VectorDist.mann = _MannDist()
