"""In-memory hybrid evidence store.

Combines dense (embedding cosine) and sparse (keyword overlap) signals,
which is the production pattern reviewers expect. The `EvidenceStore`
interface is the seam where pgvector/Chroma would plug in unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..core.embeddings import cosine, embed


@dataclass
class Document:
    doc_id: str
    text: str
    metadata: dict = field(default_factory=dict)
    vector: np.ndarray | None = None


@dataclass
class ScoredDoc:
    doc: Document
    score: float


class EvidenceStore:
    def __init__(self) -> None:
        self._docs: list[Document] = []

    def add(self, doc_id: str, text: str, metadata: dict | None = None) -> None:
        self._docs.append(
            Document(doc_id=doc_id, text=text, metadata=metadata or {}, vector=embed(text))
        )

    def _keyword_score(self, query: str, text: str) -> float:
        q = set(query.lower().split())
        t = set(text.lower().split())
        if not q:
            return 0.0
        return len(q & t) / len(q)

    def search(self, query: str, top_k: int = 3, domain: str | None = None,
               alpha: float = 0.6) -> list[ScoredDoc]:
        """Hybrid score = alpha*dense + (1-alpha)*sparse, with optional
        metadata filtering by domain."""
        qv = embed(query)
        results: list[ScoredDoc] = []
        for doc in self._docs:
            if domain and doc.metadata.get("domain") not in (None, domain):
                continue
            dense = cosine(qv, doc.vector) if doc.vector is not None else 0.0
            sparse = self._keyword_score(query, doc.text)
            score = alpha * dense + (1 - alpha) * sparse
            results.append(ScoredDoc(doc=doc, score=round(score, 4)))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def __len__(self) -> int:
        return len(self._docs)


def seed_demo_store() -> EvidenceStore:
    """Seed a small knowledge base so the demo works immediately."""
    store = EvidenceStore()
    store.add(
        "policy-001",
        "Loan applications with a debt-to-income ratio above 0.43 require "
        "manual underwriter review before approval.",
        {"domain": "underwriting", "source": "credit_policy_v3"},
    )
    store.add(
        "policy-002",
        "Applicants with a credit score below 620 are classified as high risk "
        "and must be escalated to a senior underwriter.",
        {"domain": "underwriting", "source": "credit_policy_v3"},
    )
    store.add(
        "med-001",
        "Cold-chain medical shipments must remain between 2C and 8C; any "
        "excursion beyond 30 minutes requires quality hold and investigation.",
        {"domain": "logistics", "source": "gdp_guidelines"},
    )
    store.add(
        "med-002",
        "A temperature excursion above 8C invalidates the shipment unless a "
        "stability budget review confirms product integrity.",
        {"domain": "logistics", "source": "gdp_guidelines"},
    )
    return store
