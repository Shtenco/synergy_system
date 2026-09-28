from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class SynergyEnvelope(BaseModel):
    contract_id: str
    schema_version: Literal[1] = 1
    event_id: UUID
    trace_id: UUID
    producer: str
    authority: str
    produced_at: datetime
    payload: dict[str, Any]
    payload_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_ids: list[str] = []
    parent_event_ids: list[UUID] = []
    idempotency_key: str | None = None
    state_version: str | None = None
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_payload_hash(self) -> "SynergyEnvelope":
        import json
        canonical = json.dumps(
            self.payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        expected = sha256(canonical).hexdigest()
        if expected != self.payload_sha256:
            raise ValueError("payload_sha256 does not match canonical payload")
        return self


class PositionIntent(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL", "FLAT"]
    notional: Decimal


class PortfolioDecisionPayload(BaseModel):
    decision_id: UUID
    as_of: datetime
    account_id: str
    positions: list[PositionIntent]
    rationale: list[str]
    confidence: float = Field(ge=0, le=1)
    model_refs: list[str] = []
    market_state_id: str | None = None


class ValidationMetrics(BaseModel):
    n: int = Field(ge=0)
    total_return: float
    sharpe: float
    max_drawdown: float = Field(ge=0)
    hit_rate: float = Field(ge=0, le=1)


class ValidationDecisionPayload(BaseModel):
    candidate_event_id: UUID
    gate: Literal["RESEARCH", "REJECT", "PAPER", "CANARY"]
    metrics: ValidationMetrics
    protocol_id: str
    dataset_manifest_sha256: str | None = None
    warnings: list[str] = []


class RiskDecisionPayload(BaseModel):
    source_event_id: UUID
    action: Literal["ALLOW", "RESIZE", "REJECT", "KILL_SWITCH"]
    approved_notional: Decimal
    reasons: list[str]
    metrics: dict[str, Any]
    account_state_version: str
    policy_version: str


class ExecutionSlice(BaseModel):
    venue: str
    notional: Decimal
    expected_price: Decimal
    expected_cost_bps: float = Field(ge=0)


class ExecutionPlanPayload(BaseModel):
    risk_event_id: UUID
    correlation_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    requested_notional: Decimal
    slices: list[ExecutionSlice]
    unfilled_notional: Decimal


class FillPayload(BaseModel):
    venue: str
    requested: Decimal
    filled: Decimal
    avg_price: Decimal
    fee: Decimal
    external_id: str


class ExecutionResultPayload(BaseModel):
    plan_event_id: UUID
    symbol: str
    side: Literal["BUY", "SELL"]
    requested_notional: Decimal
    filled_notional: Decimal
    fills: list[FillPayload]
    status: Literal["FILLED", "PARTIAL", "REJECTED", "FAILED"]


class SettlementEvidencePayload(BaseModel):
    settlement_id: UUID
    reference: str
    asset: str
    amount: Decimal
    provider: str
    status: Literal["SETTLED", "FAILED", "COMPENSATED"]
    occurred_at: datetime
    reconciled: bool
    reconciliation_breaks: list[str] = []
    provider_reference: str | None = None


class AccountingEntry(BaseModel):
    account: str
    side: Literal["DEBIT", "CREDIT"]
    asset: str
    amount: Decimal


class AccountingRecognitionPayload(BaseModel):
    source_settlement_event_id: UUID
    recognition_id: UUID
    classification: Literal[
        "REVENUE","EXPENSE","ASSET_TRANSFER","LIABILITY_CHANGE",
        "TRADING_PNL","CAPITAL_FLOW","NON_RECOGNIZED"
    ]
    entries: list[AccountingEntry]
    recognized_at: datetime
    accounting_period: str
    hardnav_delta: Decimal
    liquidnav_delta: Decimal = Decimal("0")
    economicnav_delta: Decimal = Decimal("0")
    policy_refs: list[str] = []


class TrustCommitmentPayload(BaseModel):
    source_event_id: UUID
    source_contract_id: str
    payload_sha256: str
    chain_id: str
    commitment_id: str
    finality_status: Literal["PENDING","FINALIZED","REORGED","REJECTED"]
    block_height: int | None = None
    tx_id: str | None = None
    authorization_profile: str | None = None


CONTRACT_PAYLOAD_MODELS = {
    "synergy.trading.portfolio-decision/v1": PortfolioDecisionPayload,
    "synergy.trading.validation-decision/v1": ValidationDecisionPayload,
    "synergy.trading.risk-decision/v1": RiskDecisionPayload,
    "synergy.trading.execution-plan/v1": ExecutionPlanPayload,
    "synergy.trading.execution-result/v1": ExecutionResultPayload,
    "synergy.settlement.evidence/v1": SettlementEvidencePayload,
    "synergy.accounting.recognition/v1": AccountingRecognitionPayload,
    "synergy.trust.commitment/v1": TrustCommitmentPayload,
}


def validate_typed_event(data: dict[str, Any]) -> SynergyEnvelope:
    envelope = SynergyEnvelope.model_validate(data)
    model = CONTRACT_PAYLOAD_MODELS.get(envelope.contract_id)
    if model is not None:
        model.model_validate(envelope.payload)
    return envelope
