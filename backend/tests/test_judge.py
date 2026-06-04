"""LLM-as-judge parsing + safe fallback behavior."""
import asyncio

from app.evaluation import judge
from app.providers.base import BaseProvider, ProviderProfile, ProviderResult
from app.schemas import DomainPolicy


class _FakeProvider(BaseProvider):
    def __init__(self, text: str) -> None:
        self.profile = ProviderProfile(name="fake", cost_per_1k_tokens=0.0,
                                       avg_latency_ms=1.0, quality=0.9)
        self._text = text

    async def complete(self, prompt: str, context: str = "") -> ProviderResult:
        return ProviderResult(text=self._text, provider="fake", cost_usd=0.0,
                              latency_ms=1.0, tokens=1)


def test_parse_valid_json():
    out = judge.parse_judge_response('here: {"faithfulness": 0.8, "policy_score": 0.9}')
    assert out["faithfulness"] == 0.8


def test_parse_rejects_garbage():
    assert judge.parse_judge_response("no json here") is None
    assert judge.parse_judge_response('{"faithfulness": 0.8}') is None  # missing policy_score


def test_llm_evaluate_uses_judge_scores_on_valid_json():
    provider = _FakeProvider('{"faithfulness": 0.95, "policy_score": 0.9, "rationale": "grounded"}')
    result = asyncio.run(
        judge.llm_evaluate(provider, "answer", "evidence", [], DomainPolicy(min_citation_coverage=0.0))
    )
    assert result is not None
    assert result.faithfulness == 0.95
    assert result.judge == "llm:fake"
    assert result.rationale == "grounded"


def test_llm_evaluate_falls_back_on_unparseable_output():
    provider = _FakeProvider("I cannot produce JSON, sorry.")
    result = asyncio.run(
        judge.llm_evaluate(provider, "answer", "evidence", [], DomainPolicy())
    )
    assert result is None  # caller then falls back to the heuristic evaluator


def test_llm_evaluate_clamps_out_of_range_scores():
    provider = _FakeProvider('{"faithfulness": 1.7, "policy_score": -0.4}')
    result = asyncio.run(
        judge.llm_evaluate(provider, "answer", "evidence", [], DomainPolicy(min_citation_coverage=0.0))
    )
    assert result is not None
    assert result.faithfulness == 1.0
    assert result.policy_score == 0.0
