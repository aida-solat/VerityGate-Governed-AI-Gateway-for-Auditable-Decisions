"""Semantic cache must partition by governance scope (no cross-policy leaks)."""
from app.cache import SemanticCache


def test_hit_within_same_scope():
    cache = SemanticCache(threshold=0.9)
    cache.put("approve the loan", {"v": 1}, scope="underwriting|low|rag=True|")
    assert cache.get("approve the loan", scope="underwriting|low|rag=True|") == {"v": 1}


def test_miss_across_different_scope():
    cache = SemanticCache(threshold=0.9)
    cache.put("approve the loan", {"v": 1}, scope="underwriting|low|rag=True|")
    # Same prompt, different governance scope -> must NOT return the cached payload.
    assert cache.get("approve the loan", scope="logistics|high|rag=True|") is None
    assert cache.get("approve the loan", scope="underwriting|high|rag=True|") is None


def test_default_scope_isolated_from_named_scope():
    cache = SemanticCache(threshold=0.9)
    cache.put("approve the loan", {"v": 1}, scope="")
    assert cache.get("approve the loan", scope="underwriting|low|rag=True|") is None
    assert cache.get("approve the loan", scope="") == {"v": 1}
