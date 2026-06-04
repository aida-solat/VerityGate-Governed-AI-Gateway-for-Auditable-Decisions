"""Policy-as-code registry.

Per-domain governance policies live as version-controlled YAML in
`app/governance/policies/`. Compliance owners can tune thresholds and banned
claims without touching application code. The registry loads them at startup
and resolves the right policy for each request's domain (falling back to the
baseline `default` policy).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from ..config import Settings
from ..schemas import DomainPolicy

POLICIES_DIR = Path(__file__).parent / "policies"


def _default_policy(settings: Settings) -> DomainPolicy:
    return DomainPolicy(
        domain="default",
        description="Baseline policy derived from settings.",
        min_faithfulness=settings.min_faithfulness,
        min_citation_coverage=settings.min_citation_coverage,
        min_policy_score=settings.min_policy_score,
        banned_claims=[
            "guaranteed", "100% safe", "no risk", "always approve", "definitely will",
        ],
    )


class PolicyRegistry:
    def __init__(self, policies: dict[str, DomainPolicy]) -> None:
        self._policies = policies

    def resolve(self, domain: str | None) -> DomainPolicy:
        """Return the policy for a domain, or the default policy."""
        if domain and domain in self._policies:
            return self._policies[domain]
        return self._policies["default"]

    def all(self) -> list[DomainPolicy]:
        # default first, then alphabetical.
        rest = sorted(d for d in self._policies if d != "default")
        return [self._policies["default"]] + [self._policies[d] for d in rest]

    def __len__(self) -> int:
        return len(self._policies)


def load_policies(settings: Settings, directory: Path | None = None) -> PolicyRegistry:
    directory = directory or POLICIES_DIR
    policies: dict[str, DomainPolicy] = {}
    if directory.exists():
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text()) or {}
            policy = DomainPolicy(**data)
            policies[policy.domain] = policy
    if "default" not in policies:
        policies["default"] = _default_policy(settings)
    return PolicyRegistry(policies)
