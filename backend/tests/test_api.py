"""End-to-end API tests over the governed pipeline + audit ledger."""
from app.db import DecisionRecord, SessionLocal


def test_low_risk_grounded_is_allowed(client):
    # Default policy (lenient baseline) on a grounded, low-risk request.
    r = client.post(
        "/ai/complete",
        json={
            "prompt": "What credit score is considered high risk for underwriting?",
            "risk_level": "low",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "allowed"
    assert body["citations"]
    assert body["evaluation"]["policy"] == "default"
    assert "decision_id" in body


def test_stricter_domain_policy_enforces_required_citations(client):
    # The underwriting policy-as-code mandates citations (require_citations);
    # the default policy does not. Same request, an extra rule fires.
    r = client.post(
        "/ai/complete",
        json={
            "prompt": "Should this borrower's loan be approved?",
            "risk_level": "low",
            "domain": "underwriting",
            "use_rag": False,
        },
    )
    body = r.json()
    assert body["evaluation"]["policy"] == "underwriting"
    assert "missing_required_citations" in body["evaluation"]["failed_checks"]
    assert body["status"] != "allowed"


def test_cache_does_not_leak_across_domains(client):
    # Identical prompt, two domains: the cache must NOT serve the first
    # domain's decision (and its policy) for the second domain.
    payload = {"prompt": "Summarize the approval criteria.", "risk_level": "low"}
    first = client.post("/ai/complete", json={**payload, "domain": "logistics"}).json()
    second = client.post("/ai/complete", json={**payload, "domain": "underwriting"}).json()
    assert first["evaluation"]["policy"] == "logistics"
    assert second["evaluation"]["policy"] == "underwriting"


def test_policies_endpoint_exposes_policy_as_code(client):
    policies = client.get("/policies").json()
    domains = {p["domain"] for p in policies}
    assert {"default", "underwriting", "logistics"} <= domains


def test_high_risk_ungrounded_is_withheld(client):
    r = client.post(
        "/ai/complete",
        json={"prompt": "Approve this claim now", "risk_level": "high", "use_rag": False},
    )
    body = r.json()
    assert body["status"] == "needs_review"
    assert "withheld" in body["output"].lower()


def test_review_queue_then_human_approve(client):
    # Create a withheld decision.
    r = client.post(
        "/ai/complete",
        json={"prompt": "Approve this loan immediately", "risk_level": "high", "use_rag": False},
    )
    decision_id = r.json()["decision_id"]

    queue = client.get("/review/queue").json()
    assert any(item["decision_id"] == decision_id for item in queue)

    approved = client.post(
        f"/review/{decision_id}",
        json={"decision": "approve", "reviewer": "tester", "note": "ok"},
    ).json()
    assert approved["status"] == "allowed"
    # Immutable original gate decision is preserved.
    assert approved["gate_status"] == "needs_review"
    assert approved["reviewer"] == "tester"


def test_ledger_chain_is_valid_after_review(client):
    v = client.get("/ledger/verify").json()
    assert v["valid"] is True


def test_tamper_detection(client):
    # Directly mutate stored output without updating its hash.
    db = SessionLocal()
    rec = db.query(DecisionRecord).first()
    assert rec is not None
    rec.output = "TAMPERED"
    db.commit()
    db.close()

    v = client.get("/ledger/verify").json()
    assert v["valid"] is False
    assert v["reason"] == "output tampered"
