from __future__ import annotations

import hashlib
import json
from datetime import datetime, UTC
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

SCHEMA = "synergy.live-economic-cycle-capture-candidate/v1"
ECONOMIC_CYCLE_V1 = "83f9c3ee0c168ca50212ebaa1e64c58c08eb87fd040a8b5f214ee4987242f3f1"
ECONOMIC_OS_RC4 = "51566c3c87f21b1a22ddef9bb6aea6abd9170042790f37ac3ff559bf7ad89c60"
HEX = frozenset("0123456789abcdef")
FORBIDDEN_EXTERNALITY_TOKENS = ("MOCK", "SYNTH", "SIMULAT", "LOCAL_ONLY", "TEST_FIXTURE")
TOP_LEVEL_FIELDS = frozenset({
    "schema", "run_id", "economic_cycle_v1_digest", "economic_os_rc4_digest", "started_at", "completed_at", "phases",
    "canonical_hard_nav_before", "canonical_hard_nav_after", "realized_external_pnl_before", "realized_external_pnl_after",
    "next_cycle_final_available_capacity", "next_cycle_capacity_status", "internal_mint_or_revaluation_counted_as_profit",
    "capture_status", "external_verification_status", "live_execution_claim", "authority", "execution_authority", "ai_authority",
    "blockchain_submission_authority", "digest",
})
BASE_PHASE_FIELDS = frozenset({"ordinal", "phase", "owner", "schema", "artifact_digest", "observed_at"})
EXTERNAL_FIELDS = frozenset({"provider", "provider_reference", "environment", "provider_evidence_digest", "verification_status"})
PHASES = (
    (1, "EXTERNAL_VALUE_EVIDENCE", "Shtenco/synergy_pay_system", "settlement.receipt/v2", True),
    (2, "REVENUE_RECOGNITION", "Shtenco/synergy_financial_os", "revenue.recognition/v2", False),
    (3, "CANONICAL_LEDGER_AND_CLOSE", "Shtenco/synergy_financial_os", "economic.cycle-trace/v6", False),
    (4, "FEE_AWARE_DISTRIBUTION_ENTITLEMENT", "Shtenco/synergy_financial_os", "distribution.budget-state/v2", False),
    (5, "CURRENT_DISTRIBUTION_CAPACITY", "Shtenco/synergy_financial_os", "distribution.available-capacity/v3", False),
    (6, "HUMAN_GOVERNANCE_HANDOFF", "Shtenco/synergy_financial_os", "distribution.execution-ticket/v3", False),
    (7, "METAPAY_SETTLEMENT", "Shtenco/synergy_pay_system", "distribution.utilization/v3", True),
    (8, "SETTLEMENT_ACCOUNTING", "Shtenco/synergy_financial_os", "distribution.fee-accounting-decision/v3", False),
    (9, "LATER_SETTLEMENT_REVERSAL", "Shtenco/synergy_pay_system", "distribution.settlement-reversal/v2", True),
    (10, "REVERSAL_ACCOUNTING", "Shtenco/synergy_financial_os", "distribution.reversal-accounting-decision/v2", False),
    (11, "ENTITLEMENT_RESTORATION", "Shtenco/synergy_financial_os", "distribution.budget-state/v3", False),
    (12, "NEXT_CYCLE_CAPACITY", "Shtenco/synergy_financial_os", "distribution.available-capacity/v4", False),
)

class LiveEconomicCycleCaptureV1Error(ValueError):
    pass


def canonical_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LiveEconomicCycleCaptureV1Error(f"{name} required")
    return value.strip()


def _hex(value: Any, name: str) -> str:
    result = _text(value, name).lower()
    if len(result) != 64 or any(ch not in HEX for ch in result):
        raise LiveEconomicCycleCaptureV1Error(f"{name} must be hex64")
    return result


def _time(value: Any, name: str) -> datetime:
    text = _text(value, name)
    if not text.endswith("Z"):
        raise LiveEconomicCycleCaptureV1Error(f"{name} must be UTC Z")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)
    if parsed.isoformat().replace("+00:00", "Z") != text:
        raise LiveEconomicCycleCaptureV1Error(f"{name} not canonical")
    return parsed


def _decimal(value: Any, name: str, *, positive: bool = False, allow_negative: bool = False) -> Decimal:
    if not isinstance(value, str) or not value:
        raise LiveEconomicCycleCaptureV1Error(f"{name} must be decimal text")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise LiveEconomicCycleCaptureV1Error(f"{name} invalid") from exc
    if not result.is_finite() or (not allow_negative and result < 0) or (positive and result <= 0):
        raise LiveEconomicCycleCaptureV1Error(f"{name} invalid amount")
    return result


def _verify_external_evidence_claim(value: Any, phase: str) -> None:
    if not isinstance(value, Mapping):
        raise LiveEconomicCycleCaptureV1Error(f"{phase} requires external evidence claim")
    if set(value) != EXTERNAL_FIELDS:
        raise LiveEconomicCycleCaptureV1Error(f"{phase} external evidence fields mismatch")
    provider = _text(value.get("provider"), f"{phase}.provider")
    reference = _text(value.get("provider_reference"), f"{phase}.provider_reference")
    environment = _text(value.get("environment"), f"{phase}.environment").upper()
    _hex(value.get("provider_evidence_digest"), f"{phase}.provider_evidence_digest")
    combined = f"{provider} {reference} {environment}".upper()
    if environment != "LIVE_EXTERNAL" or any(token in combined for token in FORBIDDEN_EXTERNALITY_TOKENS):
        raise LiveEconomicCycleCaptureV1Error(f"{phase} is not an admissible live-external evidence claim")
    if value.get("verification_status") != "PENDING_EXTERNAL_VERIFICATION":
        raise LiveEconomicCycleCaptureV1Error(f"{phase} cannot self-assert external verification")


def _required_phase_fields(phase: str, requires_external: bool) -> frozenset[str]:
    fields = set(BASE_PHASE_FIELDS)
    if requires_external:
        fields.add("external_evidence")
    if phase == "HUMAN_GOVERNANCE_HANDOFF":
        fields.update(("decision_authority", "ai_authority"))
    if phase == "LATER_SETTLEMENT_REVERSAL":
        fields.add("authorization_consumption")
    return frozenset(fields)


def verify_live_economic_cycle_capture_candidate_v1(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or payload.get("schema") != SCHEMA:
        raise LiveEconomicCycleCaptureV1Error("unsupported live cycle capture schema")
    if set(payload) != TOP_LEVEL_FIELDS:
        raise LiveEconomicCycleCaptureV1Error("capture top-level fields mismatch")
    item = dict(payload)
    supplied = item.pop("digest", None)
    if supplied != canonical_digest(item):
        raise LiveEconomicCycleCaptureV1Error("capture digest mismatch")
    if item.get("economic_cycle_v1_digest") != ECONOMIC_CYCLE_V1 or item.get("economic_os_rc4_digest") != ECONOMIC_OS_RC4:
        raise LiveEconomicCycleCaptureV1Error("protocol/release root mismatch")
    _text(item.get("run_id"), "run_id")
    started = _time(item.get("started_at"), "started_at")
    completed = _time(item.get("completed_at"), "completed_at")
    if completed <= started:
        raise LiveEconomicCycleCaptureV1Error("cycle time ordering invalid")
    phases = item.get("phases")
    if not isinstance(phases, list) or len(phases) != len(PHASES):
        raise LiveEconomicCycleCaptureV1Error("exact 12 phases required")
    times = []
    for raw, expected in zip(phases, PHASES):
        if not isinstance(raw, Mapping):
            raise LiveEconomicCycleCaptureV1Error("phase must be object")
        ordinal, phase, owner, schema, requires_external = expected
        if set(raw) != _required_phase_fields(phase, requires_external):
            raise LiveEconomicCycleCaptureV1Error(f"phase fields mismatch: {phase}")
        if (raw.get("ordinal"), raw.get("phase"), raw.get("owner"), raw.get("schema")) != (ordinal, phase, owner, schema):
            raise LiveEconomicCycleCaptureV1Error(f"phase contract mismatch: {phase}")
        _hex(raw.get("artifact_digest"), f"{phase}.artifact_digest")
        observed = _time(raw.get("observed_at"), f"{phase}.observed_at")
        times.append(observed)
        if requires_external:
            _verify_external_evidence_claim(raw.get("external_evidence"), phase)
        if phase == "HUMAN_GOVERNANCE_HANDOFF":
            if raw.get("decision_authority") not in ("HUMAN_COMMITTEE", "MULTISIG_GOVERNANCE") or raw.get("ai_authority") != "NONE":
                raise LiveEconomicCycleCaptureV1Error("governance authority invalid")
        if phase == "LATER_SETTLEMENT_REVERSAL" and raw.get("authorization_consumption") != "REMAINS_CONSUMED":
            raise LiveEconomicCycleCaptureV1Error("reversal revived authorization")
    if times != sorted(times) or times[0] < started or times[-1] > completed:
        raise LiveEconomicCycleCaptureV1Error("phase chronology invalid")
    nav_before = _decimal(item.get("canonical_hard_nav_before"), "canonical_hard_nav_before")
    nav_after = _decimal(item.get("canonical_hard_nav_after"), "canonical_hard_nav_after")
    pnl_before = _decimal(item.get("realized_external_pnl_before"), "realized_external_pnl_before", allow_negative=True)
    pnl_after = _decimal(item.get("realized_external_pnl_after"), "realized_external_pnl_after", allow_negative=True)
    next_capacity = _decimal(item.get("next_cycle_final_available_capacity"), "next_cycle_final_available_capacity", positive=True)
    if nav_after <= nav_before:
        raise LiveEconomicCycleCaptureV1Error("candidate does not show canonical HardNAV increase")
    if pnl_after <= pnl_before:
        raise LiveEconomicCycleCaptureV1Error("candidate does not show realized external P&L increase")
    if item.get("next_cycle_capacity_status") != "CAPACITY_AVAILABLE" or next_capacity <= 0:
        raise LiveEconomicCycleCaptureV1Error("positive next capacity not structurally shown")
    if _decimal(item.get("internal_mint_or_revaluation_counted_as_profit"), "internal_mint_or_revaluation_counted_as_profit") != 0:
        raise LiveEconomicCycleCaptureV1Error("internal value counted as profit")
    if item.get("capture_status") != "STRUCTURALLY_COMPLETE_PENDING_EXTERNAL_VERIFICATION":
        raise LiveEconomicCycleCaptureV1Error("capture cannot self-promote to live verified")
    if item.get("external_verification_status") != "PENDING" or item.get("live_execution_claim") is not False:
        raise LiveEconomicCycleCaptureV1Error("external verification/live claim escalation")
    if item.get("authority") != "PROVENANCE_ONLY" or item.get("execution_authority") != "NONE" or item.get("ai_authority") != "NONE" or item.get("blockchain_submission_authority") != "NONE":
        raise LiveEconomicCycleCaptureV1Error("capture authority escalation")
    item["digest"] = supplied
    return item

verify_live_economic_cycle_capture_v1 = verify_live_economic_cycle_capture_candidate_v1
