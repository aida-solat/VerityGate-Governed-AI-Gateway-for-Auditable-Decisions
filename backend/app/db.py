from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class DecisionRecord(Base):
    __tablename__ = "decisions"

    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    # Effective status (may change after human review).
    status: Mapped[str] = mapped_column(String, index=True)
    # Original automated gate outcome at creation time — immutable, hashed.
    gate_status: Mapped[str] = mapped_column(String, index=True)
    risk_level: Mapped[str] = mapped_column(String, index=True)
    provider: Mapped[str] = mapped_column(String)
    domain: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    prompt: Mapped[str] = mapped_column(String)
    output: Mapped[str] = mapped_column(String)
    evidence: Mapped[str] = mapped_column(String)

    input_hash: Mapped[str] = mapped_column(String)
    evidence_hash: Mapped[str] = mapped_column(String)
    output_hash: Mapped[str] = mapped_column(String)
    decision_hash: Mapped[str] = mapped_column(String)
    prev_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    faithfulness: Mapped[float] = mapped_column(Float)
    citation_coverage: Mapped[float] = mapped_column(Float)
    policy_score: Mapped[float] = mapped_column(Float)

    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    cached: Mapped[bool] = mapped_column(Boolean, default=False)

    reviewer: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    review_decision: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    review_note: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
