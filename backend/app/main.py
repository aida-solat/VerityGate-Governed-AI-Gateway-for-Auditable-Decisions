from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import __version__
from .api import complete, ledger, policies, review
from .api.deps import _router, _store
from .config import get_settings
from .db import engine, init_db
from .telemetry import setup_telemetry

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    setup_telemetry(app=application, engine=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    summary="Governed AI Gateway for Auditable Decisions",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complete.router)
app.include_router(ledger.router)
app.include_router(review.router)
app.include_router(policies.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": __version__,
        "tagline": "Route models. Verify evidence. Govern decisions.",
        "providers": list(_router.providers.keys()),
        "routing_strategy": settings.routing_strategy,
        "evidence_docs": len(_store),
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics", tags=["meta"])
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
