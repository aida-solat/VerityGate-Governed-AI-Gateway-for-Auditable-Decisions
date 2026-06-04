from app.evaluation import pipeline as ev
from app.schemas import Citation, DomainPolicy


def test_faithfulness_zero_without_evidence():
    assert ev.faithfulness("some answer", "") == 0.0


def test_faithfulness_high_when_output_matches_evidence():
    text = "applicants with a credit score below 620 are high risk"
    assert ev.faithfulness(text, text) > 0.9


def test_citation_coverage_zero_without_citations():
    assert ev.citation_coverage("a sentence.", []) == 0.0


def test_citation_coverage_detects_supported_sentence():
    cites = [Citation(doc_id="d1", snippet="credit score below 620 is high risk", score=0.9)]
    cov = ev.citation_coverage("A credit score below 620 is high risk.", cites)
    assert cov > 0.0


def test_policy_score_penalizes_banned_claims():
    score, hits = ev.policy_score("This is 100% safe and guaranteed.")
    assert score < 1.0
    assert hits


def test_evaluate_flags_failed_checks():
    result = ev.evaluate("ungrounded answer", "", [], DomainPolicy())
    assert not result.passed
    assert result.failed_checks
    assert result.judge == "heuristic"


def test_evaluate_judge_overrides_are_applied():
    policy = DomainPolicy(min_faithfulness=0.5)
    result = ev.evaluate(
        "answer", "evidence", [], policy,
        faithfulness_override=0.95, policy_override=0.9,
        judge_label="llm:test", rationale="looks grounded",
    )
    assert result.faithfulness == 0.95
    assert result.judge == "llm:test"
    assert result.rationale == "looks grounded"
