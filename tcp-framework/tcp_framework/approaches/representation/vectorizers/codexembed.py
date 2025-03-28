import numpy as np
from sentence_transformers import SentenceTransformer
from .code_vectorizer import CodeVectorizer, CodeVector


class CodeXEmbed(CodeVectorizer):
    def __init__(self) -> None:
        self._cache: dict[int, CodeVector] = {}
        self._model = SentenceTransformer(
            "Salesforce/SFR-Embedding-Code-400M_R",
            trust_remote_code=True,
        )  # type: ignore

    def vectorize(self, code: str) -> CodeVector:
        class_idx = code.find("class")
        if class_idx == -1:
            class_idx = 0
        code = code[class_idx:]
        h = hash(code)
        if h in self._cache:
            return self._cache[h]
        embedding = self._model.encode(code)
        self._cache[h] = embedding
        return embedding
