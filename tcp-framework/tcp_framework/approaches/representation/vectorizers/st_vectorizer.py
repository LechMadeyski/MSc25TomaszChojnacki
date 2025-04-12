import logging
from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from .code_vectorizer import CodeVectorizer


class StVectorizer(CodeVectorizer):
    # Salesforce/SFR-Embedding-Code-400M_R, intfloat/e5-base-v2, BAAI/bge-base-en-v1.5, microsoft/unixcoder-base
    def __init__(self, model: str = "BAAI/bge-base-en-v1.5", slice: Optional[int] = 100) -> None:
        self._slice = slice
        self._cache: dict[int, np.ndarray] = {}
        logging.disable(logging.CRITICAL)
        self._model = SentenceTransformer(model, trust_remote_code=True)  # type: ignore
        logging.disable(logging.NOTSET)

    def __call__(self, code: str) -> np.ndarray:
        class_idx = code.find("class")
        if class_idx == -1:
            class_idx = 0
        code = code[class_idx:]
        code = code[: self._slice] if self._slice else code
        h = hash(code)
        if h in self._cache:
            return self._cache[h]
        embedding = self._model.encode(code, normalize_embeddings=True)
        self._cache[h] = embedding
        return embedding
