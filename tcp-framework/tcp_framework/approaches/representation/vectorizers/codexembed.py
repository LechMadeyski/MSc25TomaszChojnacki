from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from .code_vectorizer import CodeVectorizer


class CodeXEmbed(CodeVectorizer):
    def __init__(self, slice: Optional[int] = None) -> None:
        self._slice = slice
        self._cache: dict[int, np.ndarray] = {}
        self._model = SentenceTransformer(
            "Salesforce/SFR-Embedding-Code-400M_R",
            trust_remote_code=True,
        )  # type: ignore

    def __call__(self, code: str) -> np.ndarray:
        class_idx = code.find("class")
        if class_idx == -1:
            class_idx = 0
        code = code[class_idx:]
        code = code[: self._slice] if self._slice else code
        h = hash(code)
        if h in self._cache:
            return self._cache[h]
        embedding = self._model.encode(code)
        self._cache[h] = embedding
        return embedding
