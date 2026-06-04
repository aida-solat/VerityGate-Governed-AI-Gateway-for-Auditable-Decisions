"""Evaluation pipeline.

Produces three independent, explainable scores. These are heuristic by
design so the demo runs offline, but each function is a clean seam where an
LLM-judge or a RAGAS-style metric would slot in for production.
"""
import re

from ..core.embeddings import cosine, embed
from ..schemas import Citation, DomainPolicy, EvaluationResult

_BANNED_CLAIMS = [
    "guaranteed", "100% safe", "no risk", "always approve", "definitely will",
]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def faithfulness(output: str, evidence: str) -> float:
    """Semantic grounding of the output in the retrieved evidence (0..1)."""
    if not output.strip():
        return 0.0
    if not evidence.strip():
        return 0.0
    return round(max(0.0, cosine(embed(output), embed(evidence))), 4)


def citation_coverage(output: str, citations: list[Citation]) -> float:
    """Fraction of output sentences that are supported by >=1 citation."""
    sents = _sentences(output)
    if not sents:
        return 0.0
    if not citations:
        return 0.0
    cit_vectors = [embed(c.snippet) for c in citations]
    supported = 0
    for sent in sents:
        sv = embed(sent)
        if any(cosine(sv, cv) >= 0.4 for cv in cit_vectors):
            supported += 1
    return round(supported / len(sents), 4)


def policy_score(output: str, banned: list[str] | None = None) -> tuple[float, list[str]]:
    """Penalize overconfident / non-compliant language. Returns (score, hits)."""
    lowered = output.lower()
    hits = [phrase for phrase in (banned or _BANNED_CLAIMS) if phrase.lower() in lowered]
    score = max(0.0, 1.0 - 0.25 * len(hits))
    return round(score, 4), hits


def evaluate(
    output: str,
    evidence: str,
    citations: list[Citation],
    policy: DomainPolicy,
    *,
    faithfulness_override: float | None = None,
    policy_override: float | None = None,
    judge_label: str = "heuristic",
    rationale: str | None = None,
) -> EvaluationResult:
    """Score an output against a domain policy.

    The faithfulness/policy scores may be supplied by an LLM judge
    (overrides); citation coverage stays a deterministic structural check.
    Thresholds and banned claims come from the resolved policy-as-code.
    """
    f = faithfulness_override if faithfulness_override is not None else faithfulness(output, evidence)
    cc = citation_coverage(output, citations)
    ps, policy_hits = policy_score(output, policy.banned_claims)
    if policy_override is not None:
        ps = policy_override

    failed: list[str] = []
    if f < policy.min_faithfulness:
        failed.append(f"faithfulness {f} < {policy.min_faithfulness}")
    if cc < policy.min_citation_coverage:
        failed.append(f"citation_coverage {cc} < {policy.min_citation_coverage}")
    if ps < policy.min_policy_score:
        failed.append(f"policy_score {ps} < {policy.min_policy_score}")
    if policy.require_citations and not citations:
        failed.append("missing_required_citations")
    for hit in policy_hits:
        failed.append(f"banned_claim:'{hit}'")

    return EvaluationResult(
        faithfulness=f,
        citation_coverage=cc,
        policy_score=ps,
        passed=len(failed) == 0,
        failed_checks=failed,
        policy=policy.domain,
        judge=judge_label,
        rationale=rationale,
    )
