from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CompensationMode(str, Enum):
    REVERSAL = "REVERSAL"
    COMPENSATING_ACTION = "COMPENSATING_ACTION"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class CompensationStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


@dataclass(frozen=True)
class CompensationRequest:
    """Control-plane request. It never mutates or deletes the original contract."""

    request_id: str
    original_contract_id: str
    correlation_id: str
    requested_by_repo: str
    requested_by_authority: str
    mode: CompensationMode
    reason: str
    requested_at: str

    def __post_init__(self) -> None:
        if not self.request_id or not self.original_contract_id or not self.reason:
            raise ValueError("compensation request is incomplete")


@dataclass(frozen=True)
class CompensationReceipt:
    request_id: str
    original_contract_id: str
    compensation_contract_id: str | None
    status: CompensationStatus
    decided_by_repo: str
    decided_by_authority: str
    decided_at: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status is CompensationStatus.APPLIED and not self.compensation_contract_id:
            raise ValueError("applied compensation requires a new compensation contract id")
        if self.compensation_contract_id == self.original_contract_id:
            raise ValueError("compensation must create a new immutable contract, never overwrite original")
