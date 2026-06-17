# VerityGate Documentation

> Built & designed by **Deciwa**.

Documentation index for VerityGate — the Governed AI Gateway for Auditable
Decisions.

## Start here

- [Project README](../README.md) — overview, pipeline, quickstart, and the
  governance principle.
- [Architecture](ARCHITECTURE.md) — system design, per-component deep dive,
  request lifecycle, and design principles (incl. production deployment diagram).
- [Deployment guide](DEPLOYMENT.md) — AWS ECS/Fargate, Azure Container Apps,
  docker-compose, CI/CD, observability setup.
- [Threat model](THREAT_MODEL.md) — STRIDE-based analysis of governance threats
  and mitigations.

## Releases

- [v0.1.0 release notes](RELEASE_NOTES_v0.1.0.md)
- [Changelog](../CHANGELOG.md)
- [Releasing guide](RELEASING.md)

## Contributing & policies

- [Contributing guide](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Security policy](../SECURITY.md)
- [License (Apache 2.0)](../LICENSE)

## Core principle

> The model may explain, but it cannot approve a high-risk decision on its own.
> Gate outcomes are decided by deterministic rules over evaluation scores and
> risk level — never by the LLM.

---

Built & designed by **Deciwa**.
