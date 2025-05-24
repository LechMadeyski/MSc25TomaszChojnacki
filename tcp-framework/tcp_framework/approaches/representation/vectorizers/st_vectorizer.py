import logging
from typing import Literal

import numpy as np
from sentence_transformers import SentenceTransformer

from ..utils.parser import extract_code_identifiers, normalize_code
from .code_vectorizer import CodeVectorizer

type Normalization = Literal["formatting", "identifiers"] | None


class StVectorizer(CodeVectorizer):
    # Salesforce/SFR-Embedding-Code-400M_R, intfloat/e5-base-v2, BAAI/bge-base-en-v1.5, microsoft/unixcoder-base
    def __init__(
        self,
        model: str = "intfloat/e5-base-v2",
        *,
        normalization: Normalization = "identifiers",
        slicing: int = 256,
        cache_limit: int = 256,
    ) -> None:
        self._normalization = normalization
        self._slicing = slicing
        self._cache_limit = cache_limit
        self._cache: dict[int, np.ndarray] = {}
        logging.disable(logging.CRITICAL)
        self._model = SentenceTransformer(model, trust_remote_code=True)  # type: ignore
        logging.disable(logging.NOTSET)

    def __call__(self, code: str) -> np.ndarray:
        class_idx = code.find("class")
        if class_idx == -1:
            class_idx = 0
        code = code[class_idx:]
        match self._normalization:
            case "formatting":
                code = normalize_code(code)
            case "identifiers":
                code = extract_code_identifiers(code)
        code = code[: self._slicing] if self._slicing else code
        h = hash(code)
        if h in self._cache:
            return self._cache[h]
        embedding = self._model.encode(code, normalize_embeddings=True)
        self._cache[h] = embedding
        while len(self._cache) > self._cache_limit:
            del self._cache[next(iter(self._cache))]
        return embedding
