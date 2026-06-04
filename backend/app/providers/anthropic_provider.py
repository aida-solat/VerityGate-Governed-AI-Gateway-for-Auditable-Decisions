import time

from .base import BaseProvider, ProviderProfile, ProviderResult


class AnthropicProvider(BaseProvider):
    """Adapter for Anthropic Claude. Instantiated only when a key is set."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620") -> None:
        self.api_key = api_key
        self.model = model
        self.profile = ProviderProfile(
            name="anthropic",
            cost_per_1k_tokens=0.30,
            avg_latency_ms=1100.0,
            quality=0.9,
        )

    async def complete(self, prompt: str, context: str = "") -> ProviderResult:
        from anthropic import AsyncAnthropic  # lazy import

        client = AsyncAnthropic(api_key=self.api_key)
        system = (
            "You are an evidence-grounded assistant. Answer ONLY using the "
            "provided context and cite it. If context is insufficient, say so."
        )
        user = f"Context:\n{context}\n\nQuestion:\n{prompt}" if context else prompt
        start = time.perf_counter()
        resp = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        latency = (time.perf_counter() - start) * 1000
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        tokens = (resp.usage.input_tokens + resp.usage.output_tokens) if resp.usage else max(1, len(text.split()))
        cost = (tokens / 1000) * self.profile.cost_per_1k_tokens
        return ProviderResult(
            text=text,
            provider=self.profile.name,
            cost_usd=round(cost, 6),
            latency_ms=latency,
            tokens=tokens,
        )
