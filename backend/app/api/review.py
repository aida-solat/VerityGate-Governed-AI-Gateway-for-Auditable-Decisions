from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.hashing import stable_hash
from ..db import DecisionRecord
from ..observability import GATE_OUTCOMES
from ..schemas import GateStatus, LedgerEntry, ReviewDecision, ReviewRequest
from .deps import get_db

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/queue", response_model=list[LedgerEntry])
def review_queue(db: Session = Depends(get_db)) -> list[LedgerEntry]:
    from ..governance import ledger
    return ledger.list_entries(db, status=GateStatus.needs_review.value)


@router.post("/{decision_id}", response_model=LedgerEntry)
def submit_review(
    decision_id: str,
    req: ReviewRequest,
    db: Session = Depends(get_db),
) -> LedgerEntry:
    """Human-in-the-loop resolution of a withheld decision."""
    rec = db.get(DecisionRecord, decision_id)
    if not rec:
        raise HTTPException(status_code=404, detail="decision not found")
    if rec.status not in (GateStatus.needs_review.value, GateStatus.warned.value):
        raise HTTPException(status_code=409, detail="decision is not awaiting review")

    note = req.note
    if req.decision == ReviewDecision.approve:
        rec.status = GateStatus.allowed.value
    elif req.decision == ReviewDecision.reject:
        rec.status = GateStatus.rejected.value
    else:  # override -> human supplies corrected output
        rec.status = GateStatus.allowed.value
        if req.corrected_output:
            # The original output stays immutable (it is hashed into the
            # chain). The human correction is recorded as a verifiable
            # annotation so audit history is never rewritten.
            note = (
                f"{note or ''} | corrected_output_hash="
                f"{stable_hash(req.corrected_output)} | corrected_output="
                f"{req.corrected_output}"
            ).strip(" |")

    rec.reviewer = req.reviewer
    rec.review_decision = req.decision.value
    rec.review_note = note
    rec.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(rec)

    GATE_OUTCOMES.labels(status=f"reviewed_{req.decision.value}").inc()

    from ..governance import ledger
    return ledger.get_entry(db, decision_id)
