"""Lightweight, dependency-free embeddings.

This is a deterministic hashing-based bag-of-words embedding so VerityGate
runs with zero external services. The interface (`embed`, `cosine`) is the
seam where you'd swap in OpenAI/Cohere/sentence-transformers in production.
"""
import hashlib
import re

import numpy as np

_DIM = 256
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _token_index(token: str) -> int:
    h = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(h, 16) % _DIM


def embed(text: str) -> np.ndarray:
    vec = np.zeros(_DIM, dtype=np.float32)
    for token in _TOKEN_RE.findall(text.lower()):
        vec[_token_index(token)] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
