from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderProfile:
    """Static characteristics the router uses to pick a provider."""
    name: str
    cost_per_1k_tokens: float  # USD
    avg_latency_ms: float
    quality: float  # 0..1 subjective quality rating
    available: bool = True


@dataclass
class ProviderResult:
    text: str
    provider: str
    cost_usd: float
    latency_ms: float
    tokens: int


class BaseProvider(ABC):
    profile: ProviderProfile

    @abstractmethod
    async def complete(self, prompt: str, context: str = "") -> ProviderResult:
        ...
