from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .enums import GateStatus, RiskLevel, ReviewDecision


class ReviewRequest(BaseModel):
    decision: ReviewDecision
    reviewer: str
    note: Optional[str] = None
    corrected_output: Optional[str] = None


class LedgerEntry(BaseModel):
    decision_id: str
    status: GateStatus
    gate_status: GateStatus
    risk_level: RiskLevel
    provider: str
    domain: Optional[str]
    input_hash: str
    evidence_hash: str
    output_hash: str
    decision_hash: str
    prev_hash: Optional[str]
    faithfulness: float
    citation_coverage: float
    policy_score: float
    cost_usd: float
    latency_ms: float
    cached: bool
    reviewer: Optional[str] = None
    review_decision: Optional[str] = None
    review_note: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
