"""LLM-as-judge evaluator.

When enabled, an LLM scores the *faithfulness* of an output against the
retrieved evidence and a *policy compliance* score. These replace the offline
heuristic scores, but the rest of the pipeline is unchanged: citation coverage
stays a deterministic structural check, and the deterministic risk gate still
makes the final allow/withhold decision. The model never gates itself.

Safety: any failure (no provider, network error, unparseable output) falls
back to the heuristic evaluator, so governance never silently degrades.
"""
from __future__ import annotations

import json
import re

from ..providers.base import BaseProvider
from ..schemas import Citation, DomainPolicy, EvaluationResult
from . import pipeline

JUDGE_PROMPT = """You are a strict compliance auditor for AI-assisted decisions.
Given an ANSWER and the EVIDENCE it should be grounded in, return ONLY a JSON
object with these float fields in [0,1]:
  "faithfulness": how fully the ANSWER is supported by the EVIDENCE (1=fully grounded, 0=fabricated)
  "policy_score": compliance with safe, non-overconfident, non-promissory language (1=clean)
  "rationale": one short sentence explaining the scores

EVIDENCE:
{evidence}

ANSWER:
{answer}

JSON:"""

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def parse_judge_response(text: str) -> dict | None:
    """Extract the JSON verdict from a model response, tolerantly."""
    match = _JSON_RE.search(text or "")
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return None
    if "faithfulness" not in data or "policy_score" not in data:
        return None
    return data


async def llm_evaluate(
    provider: BaseProvider,
    output: str,
    evidence: str,
    citations: list[Citation],
    policy: DomainPolicy,
) -> EvaluationResult | None:
    """Score with the LLM judge. Returns None on any failure so the caller
    can fall back to the heuristic evaluator."""
    try:
        prompt = JUDGE_PROMPT.format(evidence=evidence or "(none)", answer=output)
        result = await provider.complete(prompt)
        verdict = parse_judge_response(result.text)
        if verdict is None:
            return None
        return pipeline.evaluate(
            output,
            evidence,
            citations,
            policy,
            faithfulness_override=_clamp(verdict["faithfulness"]),
            policy_override=_clamp(verdict["policy_score"]),
            judge_label=f"llm:{provider.profile.name}",
            rationale=str(verdict.get("rationale", "") or "")[:300] or None,
        )
    except Exception:
        return None
