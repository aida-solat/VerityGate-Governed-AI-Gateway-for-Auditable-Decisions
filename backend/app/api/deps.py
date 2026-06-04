"""Shared singletons + FastAPI dependencies."""
from collections.abc import Generator

from ..cache import SemanticCache
from ..config import get_settings
from ..db import SessionLocal
from ..governance.policy import PolicyRegistry, load_policies
from ..providers.router import ProviderRouter
from ..rag.retriever import Retriever
from ..rag.store import seed_demo_store
from ..service import Gateway

_settings = get_settings()
_store = seed_demo_store()
_router = ProviderRouter(_settings)
_retriever = Retriever(_store)
_cache = SemanticCache(_settings.cache_similarity_threshold)
_policies = load_policies(_settings)
_gateway = Gateway(_settings, _router, _retriever, _cache, _policies)


def get_gateway() -> Gateway:
    return _gateway


def get_policies() -> PolicyRegistry:
    return _policies


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
