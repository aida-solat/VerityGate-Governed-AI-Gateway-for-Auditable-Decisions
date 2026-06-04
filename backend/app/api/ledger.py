from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..governance import ledger
from ..schemas import LedgerEntry
from .deps import get_db

router = APIRouter(prefix="/ledger", tags=["ledger"])


@router.get("", response_model=list[LedgerEntry])
def list_decisions(
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[LedgerEntry]:
    return ledger.list_entries(db, limit=limit, status=status)


@router.get("/verify")
def verify(db: Session = Depends(get_db)) -> dict:
    """Recompute the hash chain to prove the ledger hasn't been tampered with."""
    return ledger.verify_chain(db)


@router.get("/{decision_id}", response_model=LedgerEntry)
def get_decision(decision_id: str, db: Session = Depends(get_db)) -> LedgerEntry:
    entry = ledger.get_entry(db, decision_id)
    if not entry:
        raise HTTPException(status_code=404, detail="decision not found")
    return entry
