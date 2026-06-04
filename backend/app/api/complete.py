from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..schemas import CompletionRequest, CompletionResponse
from ..service import Gateway
from .deps import get_db, get_gateway

router = APIRouter(tags=["completion"])


@router.post("/ai/complete", response_model=CompletionResponse)
async def complete(
    req: CompletionRequest,
    gateway: Gateway = Depends(get_gateway),
    db: Session = Depends(get_db),
) -> CompletionResponse:
    """Governed completion: routes, retrieves, evaluates, gates, and records
    every AI-assisted decision in the audit ledger."""
    return await gateway.complete(req, db)
