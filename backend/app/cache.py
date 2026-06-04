"""In-memory semantic cache.

Returns a cached response when a new prompt is semantically near a previous
one (cosine >= threshold). Interface mirrors what a Redis-backed vector cache
would expose in production.

Semantic matching is partitioned by an exact-match governance `scope`
(domain + risk level + RAG + forced provider). Without this, the same prompt
under different governance could return a cached decision scored against the
wrong policy — a governance leak. Entries only ever match within their scope.
"""
from __future__ import annotations

import numpy as np

from .core.embeddings import cosine, embed


class SemanticCache:
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold
        self._entries: list[tuple[str, np.ndarray, dict]] = []

    def get(self, prompt: str, scope: str = "") -> dict | None:
        qv = embed(prompt)
        best, best_score = None, 0.0
        for entry_scope, vec, payload in self._entries:
            if entry_scope != scope:
                continue
            score = cosine(qv, vec)
            if score > best_score:
                best, best_score = payload, score
        if best is not None and best_score >= self.threshold:
            return best
        return None

    def put(self, prompt: str, payload: dict, scope: str = "") -> None:
        self._entries.append((scope, embed(prompt), payload))
