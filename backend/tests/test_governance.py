"""Deterministic risk gate behavior — the heart of VerityGate."""
from app.governance.risk import decide_gate
from app.schemas import EvaluationResult, GateStatus, RiskLevel


def _eval(passed: bool, failed: list[str] | None = None) -> EvaluationResult:
    return EvaluationResult(
        faithfulness=0.9 if passed else 0.2,
        citation_coverage=0.9 if passed else 0.2,
        policy_score=1.0,
        passed=passed,
        failed_checks=failed or ([] if passed else ["faithfulness 0.2 < 0.6"]),
    )


def test_clean_pass_is_allowed_at_every_risk():
    for risk in RiskLevel:
        assert decide_gate(risk, _eval(True)) == GateStatus.allowed


def test_high_risk_failure_requires_human_review():
    assert decide_gate(RiskLevel.high, _eval(False)) == GateStatus.needs_review


def test_low_risk_failure_is_warned_not_blocked():
    assert decide_gate(RiskLevel.low, _eval(False)) == GateStatus.warned


def test_medium_risk_single_failure_is_warned():
    e = _eval(False, ["citation_coverage 0.2 < 0.5"])
    assert decide_gate(RiskLevel.medium, e) == GateStatus.warned


def test_medium_risk_multiple_failures_escalate():
    e = _eval(False, ["faithfulness 0.2 < 0.6", "citation_coverage 0.2 < 0.5"])
    assert decide_gate(RiskLevel.medium, e) == GateStatus.needs_review


def test_banned_claim_is_always_rejected():
    e = _eval(False, ["banned_claim:'guaranteed'"])
    for risk in RiskLevel:
        assert decide_gate(risk, e) == GateStatus.rejected


def test_model_cannot_self_approve_high_risk_on_failure():
    # The core guarantee: a failing high-risk decision is never auto-allowed.
    assert decide_gate(RiskLevel.high, _eval(False)) != GateStatus.allowed
