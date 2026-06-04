# Security Policy

## Supported versions

VerityGate is under active development. Security fixes target the `main`
branch and the latest tagged release.

| Version | Supported |
| ------- | --------- |
| main    | yes       |
| < 0.1   | no        |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Report privately using GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability):
open the repository's **Security** tab and choose **Report a vulnerability**.

Please include:

- a description of the issue and its impact,
- steps to reproduce or a proof of concept,
- affected versions or commit, and
- any suggested mitigation.

You can expect an initial acknowledgement within a few business days. We will
work with you on a coordinated disclosure timeline and credit you in the
release notes unless you prefer to remain anonymous.

## Scope notes

VerityGate ships with a deterministic, dependency-free mock provider so it runs
without external keys. When you enable real providers, your API keys live only
in `backend/.env` (git-ignored). Never commit credentials. The decision ledger
is tamper-evident, not encrypted — treat the database as sensitive if it holds
real prompts or outputs.

---

Maintained by **Deciwa**.
