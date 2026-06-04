# Contributing to VerityGate

Thanks for your interest in VerityGate. This project values correctness and
auditability over feature count, so contributions are reviewed with the same
governance mindset the product itself embodies.

## Ground rules

- Be respectful. This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
- Keep changes focused. One logical change per pull request.
- Governance is deterministic by design. The LLM never decides gate outcomes —
  do not introduce changes that let a model approve or reject its own output.
- Every behavioral change should come with a test.

## Project layout

```
backend/   FastAPI service (providers, RAG, evaluation, governance, ledger)
frontend/  Next.js 14 dashboard (Radix UI + Tailwind)
```

The backend uses **micromamba** for environments and the frontend uses
**pnpm**. Please use these rather than pip/npm to keep lockfiles consistent.

## Local setup

Backend:

```bash
cd backend
micromamba create -y -f environment.yml      # env "veritygate" (Python 3.11)
micromamba run -n veritygate uvicorn app.main:app --port 8009
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev          # http://localhost:3009
```

## Before you open a pull request

Run the full check suite locally — CI runs the same steps.

Backend:

```bash
cd backend
micromamba run -n veritygate pytest -q
```

Frontend:

```bash
cd frontend
pnpm lint
pnpm build
```

## Pull request checklist

- [ ] Tests added or updated, and the suite passes.
- [ ] No new lint or type errors.
- [ ] Public behavior changes are reflected in the `README.md`.
- [ ] Deterministic governance guarantees are preserved.
- [ ] Commit messages are clear and scoped.

## Commit style

Short, imperative subject lines (e.g. `add per-domain policy override`,
`fix cache scope leak`). Group unrelated changes into separate commits.

## Reporting bugs and requesting features

Use the GitHub issue templates. For security issues, **do not** open a public
issue — see [SECURITY.md](SECURITY.md).

---

VerityGate is built & designed by **Deciwa**.
