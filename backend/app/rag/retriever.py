from __future__ import annotations

from ..schemas import Citation
from .store import EvidenceStore


class Retriever:
    """Turns a query into ranked citations + a context string for the model."""

    def __init__(self, store: EvidenceStore) -> None:
        self.store = store

    def retrieve(self, query: str, top_k: int = 3, domain: str | None = None
                 ) -> tuple[str, list[Citation]]:
        scored = self.store.search(query, top_k=top_k, domain=domain)
        citations = [
            Citation(doc_id=s.doc.doc_id, snippet=s.doc.text, score=s.score)
            for s in scored
            if s.score > 0
        ]
        context = "\n".join(f"[{c.doc_id}] {c.snippet}" for c in citations)
        return context, citations
