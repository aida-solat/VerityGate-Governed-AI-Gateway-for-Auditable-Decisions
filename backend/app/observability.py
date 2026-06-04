"""Prometheus metrics for VerityGate."""
from prometheus_client import Counter, Histogram

REQUESTS = Counter(
    "veritygate_requests_total", "Total completion requests", ["provider", "risk_level"]
)
GATE_OUTCOMES = Counter(
    "veritygate_gate_outcomes_total", "Gate outcomes", ["status"]
)
EVAL_FAILURES = Counter(
    "veritygate_eval_failures_total", "Evaluation check failures", ["check"]
)
CACHE_HITS = Counter("veritygate_cache_hits_total", "Semantic cache hits")
COST = Counter("veritygate_cost_usd_total", "Cumulative model cost in USD", ["provider"])
LATENCY = Histogram(
    "veritygate_latency_ms", "End-to-end request latency (ms)",
    buckets=(10, 25, 50, 100, 250, 500, 1000, 2000, 5000),
)
