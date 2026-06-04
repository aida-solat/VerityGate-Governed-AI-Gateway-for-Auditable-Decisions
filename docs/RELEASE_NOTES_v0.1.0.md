# VerityGate v0.1.0

**Governed AI Gateway for Auditable Decisions.**
Route models. Verify evidence. Govern decisions.

This is the first public release of VerityGate — a platform-layer reference
architecture that turns every AI output into an **auditable decision artifact**:
routed by risk, grounded in retrieved evidence, scored by an evaluation
pipeline, passed through **deterministic governance gates**, and recorded in a
**tamper-evident ledger** with human-in-the-loop review.

> The model may explain, but it cannot approve a high-risk decision on its own.

## Highlights

- **Risk-aware provider routing** across mock, OpenAI, and Anthropic, with a
  guaranteed mock fallback so it runs with zero API keys.
- **Hybrid RAG retrieval** (dense embeddings + sparse keyword overlap) with
  citations and per-domain filtering.
- **Evaluation pipeline** scoring faithfulness, citation coverage, and policy
  compliance — with an optional **LLM-as-judge** that auto-falls back to the
  heuristic and **never gates itself**.
- **Policy-as-code**: per-domain thresholds and banned claims in
  version-controlled YAML, exposed at `GET /policies`.
- **Deterministic risk gates**: `allowed` / `warned` / `needs_review` /
  `rejected`, decided by rules over scores and risk — never by the LLM.
- **Tamper-evident ledger** with `GET /ledger/verify` hash-chain verification.
- **Human-in-the-loop** review: approve / override / reject.
- **Scope-partitioned semantic cache** that prevents cross-domain governance
  leaks.
- **Prometheus metrics** for cost, latency, gate outcomes, and eval failures.
- **Next.js 14 + Radix UI dashboard**: playground, KPIs, review queue, ledger,
  and live chain-verification status.

## Getting started

```bash
# Backend (micromamba)
cd backend
micromamba create -y -f environment.yml
micromamba run -n veritygate uvicorn app.main:app --port 8009

# Frontend (pnpm)
cd frontend
pnpm install
pnpm dev          # http://localhost:3009
```

No API keys required — the mock provider and local SQLite ledger work out of
the box. See the [README](../README.md) and
[ARCHITECTURE](ARCHITECTURE.md) for details.

## Quality

- Backend: 34 passing pytest tests (gates, evaluation, policy, judge, cache
  partitioning, end-to-end API, tamper detection).
- Frontend: ESLint clean and a successful production build.
- CI: GitHub Actions runs the same toolchain (micromamba + pnpm) on every push
  and pull request.

## Known limitations

By design, this release is intentionally small: no multi-tenancy, RBAC, or
distributed queue, and the default embeddings/judge are interface seams rather
than production models. These are documented swap-in points, not omissions.

## License

Apache License 2.0.

---

Built & designed by **Deciwa**.
