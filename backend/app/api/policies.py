from fastapi import APIRouter, Depends, HTTPException

from ..governance.policy import PolicyRegistry
from ..schemas import DomainPolicy
from .deps import get_policies

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[DomainPolicy])
def list_policies(policies: PolicyRegistry = Depends(get_policies)) -> list[DomainPolicy]:
    """Expose the loaded policy-as-code so the governance rules are auditable."""
    return policies.all()


@router.get("/{domain}", response_model=DomainPolicy)
def get_policy(domain: str, policies: PolicyRegistry = Depends(get_policies)) -> DomainPolicy:
    resolved = policies.resolve(domain)
    if domain != "default" and resolved.domain == "default":
        raise HTTPException(status_code=404, detail="no policy for domain; default applies")
    return resolved
