from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class EpistemicState(str, Enum):
    KNOWN = "KNOWN"
    LEARNED = "LEARNED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class AuthorizationDecision(str, Enum):
    PROPOSAL_ONLY = "PROPOSAL_ONLY"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_REQUIRED = "NOT_REQUIRED"


@dataclass(frozen=True)
class Endpoint:
    repo: str
    component: str
    authority: str


@dataclass(frozen=True)
class Provenance:
    code_commit: str
    epistemic_state: EpistemicState
    source_refs: list[str] = field(default_factory=list)
    model_id: str | None = None
    data_cutoff: str | None = None


@dataclass(frozen=True)
class Authorization:
    required_authority: str
    decision: AuthorizationDecision
    granted_by: str | None = None
    grant_ref: str | None = None


@dataclass(frozen=True)
class Evidence:
    payload_hash: str
    refs: list[str] = field(default_factory=list)
    hash_alg: str = "sha256"


@dataclass(frozen=True)
class ContractEnvelope:
    contract_type: str
    producer: Endpoint
    consumer: Endpoint
    provenance: Provenance
    authorization: Authorization
    evidence: Evidence
    payload: dict[str, Any]
    correlation_id: UUID
    causation_id: UUID | None = None
    contract_id: UUID = field(default_factory=uuid4)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    schema_id: str = "synergy.contract-envelope/v1"
    contract_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        raw = asdict(self)
        raw["contract_id"] = str(self.contract_id)
        raw["correlation_id"] = str(self.correlation_id)
        raw["causation_id"] = str(self.causation_id) if self.causation_id else None
        raw["provenance"]["epistemic_state"] = self.provenance.epistemic_state.value
        raw["authorization"]["decision"] = self.authorization.decision.value
        return raw
