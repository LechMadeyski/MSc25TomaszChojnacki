from typing import Sequence
from sentence_transformers.util import cos_sim
from ...datatypes import RunContext
from ..tcp_approach import TcpApproach
from .vectorizers import CodeVectorizer, CodeVector


def _dst(e1: CodeVector, e2: CodeVector) -> float:
    return 1 - abs(cos_sim(e1, e2))


class Proposed(TcpApproach):
    def __init__(self, vectorizer: CodeVectorizer) -> None:
        self._vectorizer = vectorizer

    def prioritize(self, ctx: RunContext) -> None:
        embeddings: dict[str, CodeVector] = {}
        for tc in ctx.test_cases:
            embeddings[tc.name] = self._vectorizer.vectorize(ctx.inspect_code(tc))

        start = max(
            ctx.test_cases,
            key=lambda tc1: min(
                _dst(embeddings[tc1.name], embeddings[tc2.name])
                for tc2 in ctx.test_cases
                if tc1.name != tc2.name
            ),
        )
        prioritized = set([start])
        queue = ctx.test_cases.copy()
        queue.remove(start)
        ctx.execute(start)

        while queue:
            found = max(
                queue,
                key=lambda tc1: min(
                    _dst(embeddings[tc1.name], embeddings[tc2.name])
                    for tc2 in prioritized
                ),
            )
            prioritized.add(found)
            queue.remove(found)
            ctx.execute(found)
