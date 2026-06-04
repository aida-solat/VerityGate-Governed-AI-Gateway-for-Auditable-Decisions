from typing import Optional

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    faithfulness: float
    citation_coverage: float
    policy_score: float
    passed: bool
    failed_checks: list[str] = Field(default_factory=list)
    policy: str = "default"          # which domain policy was applied
    judge: str = "heuristic"         # "heuristic" | "llm:<provider>"
    rationale: Optional[str] = None  # judge explanation, when available
