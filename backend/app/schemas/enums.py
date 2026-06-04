from enum import Enum


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class GateStatus(str, Enum):
    allowed = "allowed"          # auto-approved
    warned = "warned"            # served but flagged
    needs_review = "needs_review"  # blocked pending human decision
    rejected = "rejected"        # hard-blocked by policy


class ReviewDecision(str, Enum):
    approve = "approve"
    override = "override"
    reject = "reject"
