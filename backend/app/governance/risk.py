"""Deterministic risk gates.

THE core principle of VerityGate: the model may explain, but it cannot
approve a high-risk decision on its own. Gate outcomes are decided by
deterministic rules over evaluation scores + risk level, never by the LLM.
"""
from ..schemas import EvaluationResult, GateStatus, RiskLevel


def decide_gate(risk_level: RiskLevel, evaluation: EvaluationResult) -> GateStatus:
    # Hard policy violations are always rejected, regardless of risk level.
    if any(c.startswith("banned_claim:") for c in evaluation.failed_checks):
        return GateStatus.rejected

    if risk_level == RiskLevel.high:
        # High stakes: anything less than a clean pass requires a human.
        return GateStatus.allowed if evaluation.passed else GateStatus.needs_review

    if risk_level == RiskLevel.medium:
        if evaluation.passed:
            return GateStatus.allowed
        # Borderline failures are served with a warning; deep failures escalate.
        if len(evaluation.failed_checks) <= 1:
            return GateStatus.warned
        return GateStatus.needs_review

    # low risk
    return GateStatus.allowed if evaluation.passed else GateStatus.warned
