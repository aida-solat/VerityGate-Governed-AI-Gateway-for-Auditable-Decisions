# VerityGate Threat Model

> Built & designed by **Deciwa**.

This document enumerates key threats to VerityGate's governance guarantees and
the mitigations in place. It follows a STRIDE-like classification applied to an
AI gateway that must guarantee **deterministic, auditable decision governance**.

---

## System boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│  Trust boundary: internal network / VPC                          │
│                                                                 │
│  ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌──────────────┐ │
│  │ Frontend │──▶│ Backend │──▶│ Postgres │   │ Redis cache  │ │
│  └──────────┘   │ (FastAPI)│   │ + pgvector│   └──────────────┘ │
│                 └────┬─────┘   └──────────┘                     │
│                      │                                          │
│                 ┌────▼─────┐                                    │
│                 │ LLM APIs │ (external, untrusted output)       │
│                 └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Threats and mitigations

### T1 — Prompt injection / jailbreak (Spoofing, Tampering)

| | |
|---|---|
| **Risk** | Attacker crafts a prompt that causes the model to produce harmful output that bypasses governance. |
| **Impact** | High — an ungrounded answer could be auto-approved. |
| **Mitigation** | The gate is deterministic: it reads evaluation scores over the model output, never the output's own assertion about compliance. Even a perfect jailbreak that produces confident but ungrounded text fails the faithfulness and citation checks. The model cannot self-approve. |

### T2 — Ledger tampering (Tampering)

| | |
|---|---|
| **Risk** | An insider or compromised database mutates a historical decision record. |
| **Impact** | High — audit trail is invalidated. |
| **Mitigation** | Each record's `decision_hash` covers `input_hash + evidence_hash + output_hash + gate_status + prev_hash`. Any edit to content or ordering breaks the chain, detectable via `GET /ledger/verify`. In production, Postgres WAL archiving and read-replica comparison add defense-in-depth. |

### T3 — Cache poisoning (Tampering)

| | |
|---|---|
| **Risk** | Attacker finds a prompt that lands in the cache with a permissive policy scope, then retrieves it under a stricter domain. |
| **Impact** | Medium — cross-domain governance leak. |
| **Mitigation** | Cache is partitioned by an exact-match `scope = domain|risk_level|use_rag|provider`. Only responses with `status=allowed` are cached. A cache hit under a different scope is impossible by design. Redis ACLs restrict cache writes to the backend service account. |

### T4 — Model denial-of-service (Denial of Service)

| | |
|---|---|
| **Risk** | Expensive prompts overwhelm the provider budget or cause latency spikes. |
| **Impact** | Medium — cost blowup or service degradation. |
| **Mitigation** | Risk-aware routing sends high-risk requests to the mock provider by default (zero-cost, deterministic). Prometheus alerts on `veritygate_cost_usd_total` rate and `veritygate_latency_ms` P95. Future: per-tenant rate limits at the ALB/Container App ingress. |

### T5 — Provider key exfiltration (Information Disclosure)

| | |
|---|---|
| **Risk** | API keys leaked through logs, env dumps, or container escape. |
| **Impact** | High — unauthorized spend, data exposure. |
| **Mitigation** | Keys stored in secrets manager (GitHub Actions secrets, AWS Secrets Manager / Azure Key Vault), never in source or images. `.env` is git-ignored. CloudWatch/Log Analytics redact known key patterns. Container runs as non-root with read-only FS. |

### T6 — Evaluation bypass via LLM judge manipulation (Elevation of Privilege)

| | |
|---|---|
| **Risk** | If the LLM judge is used, an adversary crafts output that tricks the judge into returning inflated scores. |
| **Impact** | Medium — inflated scores could auto-approve a borderline response. |
| **Mitigation** | The judge only *scores*; it does not decide the gate. Even inflated scores are bounded by the deterministic gate rules. Citation coverage is always a structural (non-LLM) check. When the judge is unavailable or returns unparseable output, the system falls back to the heuristic — never silently passes. |

### T7 — Unauthorized review actions (Spoofing, Elevation of Privilege)

| | |
|---|---|
| **Risk** | An unauthenticated actor approves or rejects decisions in the review queue. |
| **Impact** | High — governance decisions made without accountability. |
| **Mitigation** | Current: `reviewer` field is caller-supplied (suitable for internal single-tenant). Production hardening: integrate with OIDC/SSO at the ingress, validate JWT claims, and record the authenticated principal. The original `gate_status` remains in the hash chain regardless of the review. |

### T8 — Supply chain compromise (Tampering)

| | |
|---|---|
| **Risk** | Malicious dependency injected via pip, npm, or container base image. |
| **Impact** | High — arbitrary code execution in the gateway. |
| **Mitigation** | Pinned dependency versions in `requirements.txt` and `pnpm-lock.yaml`. GitHub Dependabot enabled. Multi-stage Docker builds with minimal runtime images (`python:3.11-slim`, `node:20-alpine`). Container scanning in CI (future: Trivy/Snyk step). |

---

## Residual risks (accepted, documented)

- **No RBAC or multi-tenancy** — by design (see Design non-goals). Deploy one instance per tenant or add an auth layer.
- **Heuristic embeddings** — deterministic but low-fidelity. A swap to a real model improves scoring accuracy but does not weaken the gate's determinism.
- **SQLite in dev** — no encryption at rest; production Postgres uses TLS and managed encryption.

---

## Review cadence

This threat model should be revisited when:
- A new provider or evaluator is added.
- Networking changes (multi-region, public exposure).
- RBAC or multi-tenancy is introduced.

---

Built & designed by **Deciwa**.
