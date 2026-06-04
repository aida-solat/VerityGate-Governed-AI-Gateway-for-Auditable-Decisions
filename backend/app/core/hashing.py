from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_hash(payload: Any) -> str:
    """Deterministic SHA-256 of any JSON-serializable payload.

    Used to build the tamper-evident decision ledger: each artifact
    (input, evidence, output, final decision) is hashed independently,
    and entries are chained via prev_hash to detect mutation.
    """
    if isinstance(payload, str):
        data = payload.encode("utf-8")
    else:
        data = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def chain_hash(prev_hash: str | None, *parts: str) -> str:
    """Build a decision hash that links to the previous ledger entry."""
    joined = "|".join([prev_hash or "GENESIS", *parts])
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
