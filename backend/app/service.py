"""Gateway orchestration: the end-to-end VerityGate pipeline.

route -> retrieve -> complete -> evaluate -> gate -> ledger -> observe
"""
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from .cache import SemanticCache
from .config import Settings
from .evaluation import judge as llm_judge
from .evaluation import pipeline as evaluation
from .governance import ledger
from .governance.policy import PolicyRegistry
from .governance.risk import decide_gate
from .observability import (
    CACHE_HITS,
    COST,
    EVAL_FAILURES,
    GATE_OUTCOMES,
    LATENCY,
    REQUESTS,
)
from .providers.router import ProviderRouter
from .rag.retriever import Retriever
from .schemas import CompletionRequest, CompletionResponse, GateStatus


class Gateway:
    def __init__(self, settings: Settings, router: ProviderRouter,
                 retriever: Retriever, cache: SemanticCache,
                 policies: PolicyRegistry) -> None:
        self.settings = settings
        self.router = router
        self.retriever = retriever
        self.cache = cache
        self.policies = policies

    async def complete(self, req: CompletionRequest, db: Session) -> CompletionResponse:
        import time
        start = time.perf_counter()

        # 0. Semantic cache lookup (partitioned by governance scope so a
        #    cached decision can never leak across domains/policies).
        scope = f"{req.domain or ''}|{req.risk_level.value}|rag={req.use_rag}|{req.provider or ''}"
        cached_payload = self.cache.get(req.prompt, scope=scope)
        if cached_payload is not None:
            CACHE_HITS.inc()
            resp = CompletionResponse(**cached_payload)
            resp.cached = True
            resp.decision_id = uuid.uuid4().hex
            resp.created_at = datetime.utcnow()
            return resp

        # 1. Route to a provider based on strategy + risk
        provider = self.router.select(req.risk_level, forced=req.provider)
        REQUESTS.labels(provider=provider.profile.name, risk_level=req.risk_level.value).inc()

        # 2. Retrieve evidence
        context, citations = ("", [])
        if req.use_rag:
            context, citations = self.retriever.retrieve(req.prompt, domain=req.domain)

        # 3. Model call
        result = await provider.complete(req.prompt, context=context)
        COST.labels(provider=result.provider).inc(result.cost_usd)

        # 4. Evaluate against the domain's policy-as-code (LLM judge if enabled,
        #    otherwise the deterministic heuristic; judge failures fall back).
        policy = self.policies.resolve(req.domain)
        evaluation_result = None
        if self.settings.use_llm_judge:
            evaluation_result = await llm_judge.llm_evaluate(
                provider, result.text, context, citations, policy
            )
        if evaluation_result is None:
            evaluation_result = evaluation.evaluate(
                result.text, context, citations, policy
            )
        for check in evaluation_result.failed_checks:
            EVAL_FAILURES.labels(check=check.split()[0].split(":")[0]).inc()

        # 5. Deterministic risk gate
        status = decide_gate(req.risk_level, evaluation_result)
        GATE_OUTCOMES.labels(status=status.value).inc()

        # Blocked outputs are not surfaced verbatim to the caller.
        surfaced = result.text
        if status in (GateStatus.needs_review, GateStatus.rejected):
            surfaced = (
                f"[{status.value}] Output withheld pending governance. "
                f"Failed checks: {', '.join(evaluation_result.failed_checks) or 'risk policy'}."
            )

        latency_ms = (time.perf_counter() - start) * 1000
        LATENCY.observe(latency_ms)

        decision_id = uuid.uuid4().hex

        # 6. Record in tamper-evident ledger
        ledger.record_decision(
            db,
            decision_id=decision_id,
            status=status,
            risk_level=req.risk_level,
            provider=result.provider,
            domain=req.domain,
            prompt=req.prompt,
            output=result.text,
            evidence=context,
            citations=citations,
            evaluation=evaluation_result,
            cost_usd=result.cost_usd,
            latency_ms=latency_ms,
            cached=False,
        )

        response = CompletionResponse(
            decision_id=decision_id,
            status=status,
            output=surfaced,
            provider=result.provider,
            risk_level=req.risk_level,
            citations=citations,
            evaluation=evaluation_result,
            cost_usd=result.cost_usd,
            latency_ms=round(latency_ms, 2),
            cached=False,
            created_at=datetime.utcnow(),
        )

        # Only cache clean, auto-allowed responses, within their scope.
        if status == GateStatus.allowed:
            self.cache.put(req.prompt, response.model_dump(), scope=scope)

        return response
