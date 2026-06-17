"""Redis-backed semantic cache with governance scope partitioning.

Production upgrade of the in-memory cache. Stores embeddings + payloads in
Redis hashes keyed by scope, enabling horizontal scaling (multiple backend
replicas share the same cache). Falls back to the in-memory SemanticCache
when REDIS_URL is empty — zero-config local development still works.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

import numpy as np

from .config import get_settings
from .core.embeddings import cosine, embed

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        import redis
        settings = get_settings()
        _redis_client = redis.from_url(
            settings.redis_url, decode_responses=True, socket_timeout=2
        )
    return _redis_client


class RedisSemanticCache:
    """Scope-partitioned semantic cache backed by Redis sorted sets."""

    PREFIX = "vg:cache:"

    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def _key(self, scope: str) -> str:
        return f"{self.PREFIX}{scope}"

    def get(self, prompt: str, scope: str = "") -> Optional[dict]:
        try:
            r = _get_redis()
            key = self._key(scope)
            entries = r.hgetall(key)
            if not entries:
                return None

            qv = embed(prompt)
            best, best_score = None, 0.0

            for _id, raw in entries.items():
                entry = json.loads(raw)
                vec = np.array(entry["vec"], dtype=np.float32)
                score = cosine(qv, vec)
                if score > best_score:
                    best, best_score = entry["payload"], score

            if best is not None and best_score >= self.threshold:
                return best
            return None
        except Exception:
            logger.warning("Redis cache read failed, returning miss", exc_info=True)
            return None

    def put(self, prompt: str, payload: dict, scope: str = "") -> None:
        try:
            r = _get_redis()
            key = self._key(scope)
            vec = embed(prompt).tolist()
            entry_id = f"{len(r.hgetall(key)):06d}"
            r.hset(key, entry_id, json.dumps({"vec": vec, "payload": payload}))
        except Exception:
            logger.warning("Redis cache write failed", exc_info=True)


def create_cache(threshold: float):
    """Factory: returns RedisSemanticCache if redis_url is set, else in-memory."""
    settings = get_settings()
    if settings.redis_url:
        logger.info("Using Redis-backed semantic cache at %s", settings.redis_url)
        return RedisSemanticCache(threshold)
    else:
        from .cache import SemanticCache
        logger.info("Using in-memory semantic cache (no REDIS_URL configured)")
        return SemanticCache(threshold)
