# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Apache 2.0 license, contribution guide, code of conduct, and security policy.
- Issue and pull request templates.

## [0.1.0] - 2026-06-04

### Added
- Risk-aware provider router with mock, OpenAI, and Anthropic providers and a
  guaranteed mock fallback.
- Hybrid dense + sparse RAG retrieval with citations and per-domain filtering.
- Evaluation pipeline scoring faithfulness, citation coverage, and policy
  compliance, with an optional LLM-as-judge and automatic heuristic fallback.
- Policy-as-code: per-domain governance thresholds and banned claims loaded
  from version-controlled YAML, exposed at `GET /policies`.
- Deterministic risk gates (`allowed` / `warned` / `needs_review` / `rejected`)
  decided by rules over scores and risk level — never by the LLM.
- Tamper-evident, hash-chained decision ledger with `GET /ledger/verify`.
- Human-in-the-loop review workflow (approve / override / reject).
- Semantic cache partitioned by governance scope to prevent cross-domain leaks.
- Prometheus metrics for cost, latency, gate outcomes, and evaluation failures.
- Next.js 14 dashboard (Radix UI + Tailwind) with playground, KPIs, review
  queue, ledger view, and chain-verification status.
- pytest suite and GitHub Actions CI (micromamba backend, pnpm frontend).

[Unreleased]: https://github.com/deciwa/veritygate/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/deciwa/veritygate/releases/tag/v0.1.0
