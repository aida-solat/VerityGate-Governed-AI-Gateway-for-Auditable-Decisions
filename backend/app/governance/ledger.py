"""Tamper-evident decision ledger.

Every AI-assisted decision is recorded as an immutable, hash-chained entry.
Each entry's decision_hash links to the previous entry's hash, so any
post-hoc mutation of history is detectable (verify_chain).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.hashing import chain_hash, stable_hash
from ..db import DecisionRecord
from ..schemas import (
    Citation,
    EvaluationResult,
    GateStatus,
    LedgerEntry,
    RiskLevel,
)


def _to_entry(rec: DecisionRecord) -> LedgerEntry:
    return LedgerEntry(
        decision_id=rec.decision_id,
        status=GateStatus(rec.status),
        gate_status=GateStatus(rec.gate_status),
        risk_level=RiskLevel(rec.risk_level),
        provider=rec.provider,
        domain=rec.domain,
        input_hash=rec.input_hash,
        evidence_hash=rec.evidence_hash,
        output_hash=rec.output_hash,
        decision_hash=rec.decision_hash,
        prev_hash=rec.prev_hash,
        faithfulness=rec.faithfulness,
        citation_coverage=rec.citation_coverage,
        policy_score=rec.policy_score,
        cost_usd=rec.cost_usd,
        latency_ms=rec.latency_ms,
        cached=rec.cached,
        reviewer=rec.reviewer,
        review_decision=rec.review_decision,
        review_note=rec.review_note,
        created_at=rec.created_at,
        reviewed_at=rec.reviewed_at,
    )


def record_decision(
    db: Session,
    *,
    decision_id: str,
    status: GateStatus,
    risk_level: RiskLevel,
    provider: str,
    domain: str | None,
    prompt: str,
    output: str,
    evidence: str,
    citations: list[Citation],
    evaluation: EvaluationResult,
    cost_usd: float,
    latency_ms: float,
    cached: bool,
) -> DecisionRecord:
    prev = db.execute(
        select(DecisionRecord).order_by(DecisionRecord.created_at.desc())
    ).scalars().first()
    prev_hash = prev.decision_hash if prev else None

    input_hash = stable_hash({"prompt": prompt, "risk": risk_level.value, "domain": domain})
    evidence_hash = stable_hash([c.model_dump() for c in citations])
    output_hash = stable_hash(output)
    decision_hash = chain_hash(
        prev_hash, input_hash, evidence_hash, output_hash, status.value
    )

    rec = DecisionRecord(
        decision_id=decision_id,
        status=status.value,
        gate_status=status.value,
        risk_level=risk_level.value,
        provider=provider,
        domain=domain,
        prompt=prompt,
        output=output,
        evidence=evidence,
        input_hash=input_hash,
        evidence_hash=evidence_hash,
        output_hash=output_hash,
        decision_hash=decision_hash,
        prev_hash=prev_hash,
        faithfulness=evaluation.faithfulness,
        citation_coverage=evaluation.citation_coverage,
        policy_score=evaluation.policy_score,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        cached=cached,
        created_at=datetime.utcnow(),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_entry(db: Session, decision_id: str) -> LedgerEntry | None:
    rec = db.get(DecisionRecord, decision_id)
    return _to_entry(rec) if rec else None


def list_entries(db: Session, limit: int = 100, status: str | None = None) -> list[LedgerEntry]:
    stmt = select(DecisionRecord).order_by(DecisionRecord.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(DecisionRecord.status == status)
    return [_to_entry(r) for r in db.execute(stmt).scalars().all()]


def verify_chain(db: Session) -> dict:
    """Recompute the hash chain to detect tampering."""
    recs = db.execute(
        select(DecisionRecord).order_by(DecisionRecord.created_at.asc())
    ).scalars().all()
    prev_hash = None
    for rec in recs:
        # 1. Recompute artifact hashes from raw stored fields to catch edits
        #    that touch the content but not the stored hash.
        if stable_hash(rec.output) != rec.output_hash:
            return {"valid": False, "broken_at": rec.decision_id,
                    "reason": "output tampered", "entries": len(recs)}
        recomputed_input = stable_hash(
            {"prompt": rec.prompt, "risk": rec.risk_level, "domain": rec.domain}
        )
        if recomputed_input != rec.input_hash:
            return {"valid": False, "broken_at": rec.decision_id,
                    "reason": "input tampered", "entries": len(recs)}

        # 2. Validate the chain linkage.
        expected = chain_hash(
            prev_hash, rec.input_hash, rec.evidence_hash, rec.output_hash, rec.gate_status
        )
        if expected != rec.decision_hash:
            return {"valid": False, "broken_at": rec.decision_id,
                    "reason": "chain broken", "entries": len(recs)}
        prev_hash = rec.decision_hash
    return {"valid": True, "broken_at": None, "entries": len(recs)}
