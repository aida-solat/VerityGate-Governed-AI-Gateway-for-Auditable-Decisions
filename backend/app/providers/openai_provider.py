import time

from .base import BaseProvider, ProviderProfile, ProviderResult


class OpenAIProvider(BaseProvider):
    """Adapter for OpenAI. Only instantiated when an API key is configured."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model
        self.profile = ProviderProfile(
            name="openai",
            cost_per_1k_tokens=0.15,
            avg_latency_ms=900.0,
            quality=0.85,
        )

    async def complete(self, prompt: str, context: str = "") -> ProviderResult:
        from openai import AsyncOpenAI  # imported lazily to keep core dep-free

        client = AsyncOpenAI(api_key=self.api_key)
        system = (
            "You are an evidence-grounded assistant. Answer ONLY using the "
            "provided context and cite it. If context is insufficient, say so."
        )
        user = f"Context:\n{context}\n\nQuestion:\n{prompt}" if context else prompt
        start = time.perf_counter()
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        latency = (time.perf_counter() - start) * 1000
        text = resp.choices[0].message.content or ""
        tokens = resp.usage.total_tokens if resp.usage else max(1, len(text.split()))
        cost = (tokens / 1000) * self.profile.cost_per_1k_tokens
        return ProviderResult(
            text=text,
            provider=self.profile.name,
            cost_usd=round(cost, 6),
            latency_ms=latency,
            tokens=tokens,
        )
