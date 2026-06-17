from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration. All values have defaults so VerityGate runs
    out-of-the-box with the mock provider and a local SQLite ledger."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VerityGate"
    environment: str = "development"

    database_url: str = "sqlite:///./veritygate.db"

    routing_strategy: str = "risk"  # cost | latency | quality | risk

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Evaluation gate thresholds (0..1) — baseline defaults; per-domain
    # policy-as-code files (app/governance/policies/*.yaml) override these.
    min_faithfulness: float = 0.6
    min_citation_coverage: float = 0.5
    min_policy_score: float = 0.7

    # LLM-as-judge: when enabled (and a provider key is configured) an LLM
    # scores faithfulness/policy instead of the offline heuristic. Falls back
    # to the heuristic automatically if the judge is unavailable or errors.
    use_llm_judge: bool = False
    judge_model: str = "gpt-4o-mini"

    # Semantic cache — Redis-backed in production, in-memory fallback in dev
    cache_similarity_threshold: float = 0.92
    redis_url: str = ""  # e.g. redis://localhost:6379/0; empty = in-memory fallback

    # OpenTelemetry
    otel_enabled: bool = False
    otel_exporter_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "veritygate-backend"


@lru_cache
def get_settings() -> Settings:
    return Settings()
