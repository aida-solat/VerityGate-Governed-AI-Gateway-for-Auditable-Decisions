from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import GateStatus, RiskLevel
from .evaluation_result import EvaluationResult


class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="The user/application prompt.")
    risk_level: RiskLevel = RiskLevel.low
    domain: Optional[str] = Field(None, description="Vertical context, e.g. 'underwriting'.")
    use_rag: bool = True
    provider: Optional[str] = Field(None, description="Force a provider; otherwise router decides.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    doc_id: str
    snippet: str
    score: float


class CompletionResponse(BaseModel):
    decision_id: str
    status: GateStatus
    output: str
    provider: str
    risk_level: RiskLevel
    citations: list[Citation] = Field(default_factory=list)
    evaluation: EvaluationResult
    cost_usd: float
    latency_ms: float
    cached: bool = False
    created_at: datetime
