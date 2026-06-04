import asyncio
import time

from .base import BaseProvider, ProviderProfile, ProviderResult


class MockProvider(BaseProvider):
    """Deterministic offline provider so VerityGate runs without API keys.

    It echoes a grounded answer that cites the provided context, which lets
    the evaluation + governance pipeline be exercised end-to-end.
    """

    def __init__(self) -> None:
        self.profile = ProviderProfile(
            name="mock",
            cost_per_1k_tokens=0.0,
            avg_latency_ms=20.0,
            quality=0.55,
        )

    async def complete(self, prompt: str, context: str = "") -> ProviderResult:
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        if context:
            answer = (
                f"Based on the retrieved evidence, here is a grounded response to: "
                f"'{prompt.strip()[:120]}'. Supporting context: {context.strip()[:240]}"
            )
        else:
            answer = (
                f"[no evidence retrieved] Tentative response to: "
                f"'{prompt.strip()[:120]}'."
            )
        tokens = max(1, len(answer.split()))
        latency = (time.perf_counter() - start) * 1000
        return ProviderResult(
            text=answer,
            provider=self.profile.name,
            cost_usd=0.0,
            latency_ms=latency,
            tokens=tokens,
        )
