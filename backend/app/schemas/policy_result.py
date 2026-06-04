from pydantic import BaseModel, Field


class DomainPolicy(BaseModel):
    """Policy-as-code: per-domain governance thresholds + banned claims.

    Loaded from app/governance/policies/*.yaml so compliance rules live in
    version-controlled config rather than scattered through code."""
    domain: str = "default"
    description: str = ""
    min_faithfulness: float = 0.6
    min_citation_coverage: float = 0.5
    min_policy_score: float = 0.7
    require_citations: bool = False
    banned_claims: list[str] = Field(default_factory=list)
