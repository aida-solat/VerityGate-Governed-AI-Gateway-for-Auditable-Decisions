from __future__ import annotations

from ..config import Settings
from ..schemas import RiskLevel
from .anthropic_provider import AnthropicProvider
from .base import BaseProvider
from .mock import MockProvider
from .openai_provider import OpenAIProvider


class ProviderRouter:
    """Selects a provider per request based on a configurable strategy.

    Strategies:
      - cost     : cheapest available provider
      - latency  : lowest expected latency
      - quality  : highest quality rating
      - risk     : high-risk requests get the highest-quality provider;
                   low-risk requests favor cost. This is the architect-level
                   default: route by stakes, not just price.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers: dict[str, BaseProvider] = {}

        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(settings.openai_api_key)
        if settings.anthropic_api_key:
            self.providers["anthropic"] = AnthropicProvider(settings.anthropic_api_key)

        # Mock is always present as a guaranteed fallback.
        self.providers["mock"] = MockProvider()

    def available(self) -> list[BaseProvider]:
        return [p for p in self.providers.values() if p.profile.available]

    def select(self, risk_level: RiskLevel, forced: str | None = None) -> BaseProvider:
        if forced and forced in self.providers:
            return self.providers[forced]

        candidates = self.available()
        strategy = self.settings.routing_strategy

        if strategy == "cost":
            return min(candidates, key=lambda p: p.profile.cost_per_1k_tokens)
        if strategy == "latency":
            return min(candidates, key=lambda p: p.profile.avg_latency_ms)
        if strategy == "quality":
            return max(candidates, key=lambda p: p.profile.quality)

        # risk-aware (default)
        if risk_level == RiskLevel.high:
            return max(candidates, key=lambda p: p.profile.quality)
        if risk_level == RiskLevel.medium:
            return max(candidates, key=lambda p: p.profile.quality - p.profile.cost_per_1k_tokens)
        return min(candidates, key=lambda p: p.profile.cost_per_1k_tokens)
