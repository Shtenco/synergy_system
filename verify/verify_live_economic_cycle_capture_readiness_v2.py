#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "live_economic_cycle_capture_readiness_v2.json"

EXPECTED_DIGEST = "94ac1c5a03218c7e680ff85aa7e68cc072afdbd04628b76366139bf57193d21f"
EXPECTED_SCHEMA = "synergy.live-economic-cycle-capture-readiness/v2"
EXPECTED_PREVIOUS = "252fe1f12f326a6b31d18bb9b16f2bd31a8a72d12ad2053ae437864db8ef2eef"
EXPECTED_RC5 = "b06425fdba3b69e1371c987714176d0435f90b511a7167abd13a4fb0a91476b8"
EXPECTED_IMPLEMENTATION = "390a00800bd26169d0e62a0d9853f6604594190f"
EXPECTED_TESTS = "194513b06ff5b30fa5c7e5a6ebad80a80b4d12af"
EXPECTED_AUDIT = "26867356d4bed8c6fbc7b2da8d9d0e83a4b53350dd8e8e6d6d88ef2eb81d7d47"
EXPECTED_AUDIT_SCOPE = "TARGETED_AUDIT_NOT_EXHAUSTIVE_REPOSITORY_CONTENT_PROOF"
EXPECTED_BLOCKER = "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED"
EXPECTED_STATUS = "HARDENED_CAPTURE_READY_NO_ADMISSIBLE_EXISTING_LIVE_FIXTURE"
EXPECTED_CANDIDATES = (
    ("fixtures/conformance/settlement_receipt_v2_revenue.json", "0f9235d56e8f757479d5ce3e8472f8e480e04b62", "CONFORMANCE_FIXTURE_NOT_LIVE"),
    ("config/live-manifest.example.json", "f6f2e08aae243e65e409e740fbd7a0eeba1f7666", "EXAMPLE_TEMPLATE_NOT_LIVE"),
    ("src/synergy_pay/providers/mock.py", "cdf3872e2afc9f8d103d2a8e6ac730c24d4a4c16", "MOCK_PROVIDER_IMPLEMENTATION_NOT_SETTLEMENT_EVIDENCE"),
)
EXPECTED_GUARANTEES = (
    "EXACT_TOP_LEVEL_FIELD_SET_ENFORCED",
    "EXACT_PHASE_FIELD_SET_ENFORCED",
    "EXACT_EXTERNAL_EVIDENCE_FIELD_SET_ENFORCED",
    "HIDDEN_LIVE_STATUS_FIELD_REJECTED_AFTER_FRESH_REHASH",
    "HIDDEN_PHASE_EXECUTION_AUTHORITY_REJECTED_AFTER_FRESH_REHASH",
    "HIDDEN_PROVIDER_VERIFICATION_FIELD_REJECTED_AFTER_FRESH_REHASH",
)


class ReadinessV2Error(ValueError):
    pass


def canonical_digest(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("digest", None)
    encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_readiness_v2(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReadinessV2Error("readiness must be object")
    supplied = value.get("digest")
    computed = canonical_digest(value)
    if supplied != EXPECTED_DIGEST or computed != EXPECTED_DIGEST:
        raise ReadinessV2Error("readiness digest mismatch")
    if value.get("schema") != EXPECTED_SCHEMA:
        raise ReadinessV2Error("schema mismatch")
    if value.get("previous_readiness_digest") != EXPECTED_PREVIOUS:
        raise ReadinessV2Error("previous readiness mismatch")
    if value.get("economic_os_rc5_digest") != EXPECTED_RC5:
        raise ReadinessV2Error("RC5 root mismatch")
    if value.get("implementation_blob_sha") != EXPECTED_IMPLEMENTATION:
        raise ReadinessV2Error("implementation identity mismatch")
    if value.get("test_blob_sha") != EXPECTED_TESTS:
        raise ReadinessV2Error("test identity mismatch")
    if value.get("targeted_metapay_audit_digest") != EXPECTED_AUDIT:
        raise ReadinessV2Error("targeted audit root mismatch")
    if value.get("targeted_metapay_audit_scope") != EXPECTED_AUDIT_SCOPE:
        raise ReadinessV2Error("targeted audit scope mismatch")
    if value.get("capture_protocol_status") != EXPECTED_STATUS:
        raise ReadinessV2Error("status promotion or mismatch")
    if value.get("current_blocker") != EXPECTED_BLOCKER or value.get("blocker_removed") is not False:
        raise ReadinessV2Error("live cycle blocker mismatch")
    if value.get("external_verification_status") != "NOT_EXECUTED" or value.get("live_execution_claim") is not False:
        raise ReadinessV2Error("live/external verification escalation")
    if (
        value.get("authority") != "PROVENANCE_ONLY"
        or value.get("execution_authority") != "NONE"
        or value.get("ai_authority") != "NONE"
        or value.get("blockchain_submission_authority") != "NONE"
    ):
        raise ReadinessV2Error("authority escalation")

    candidates = value.get("inadmissible_known_candidates")
    observed = tuple((x.get("path"), x.get("blob_sha"), x.get("classification")) for x in candidates) if isinstance(candidates, list) else ()
    if observed != EXPECTED_CANDIDATES:
        raise ReadinessV2Error("known candidate classification mismatch")
    guarantees = value.get("hardening_guarantees")
    if tuple(guarantees) != EXPECTED_GUARANTEES if isinstance(guarantees, list) else True:
        raise ReadinessV2Error("hardening guarantees mismatch")

    return {
        "status": "PASS",
        "readiness_digest": EXPECTED_DIGEST,
        "capture_protocol_status": EXPECTED_STATUS,
        "current_blocker": EXPECTED_BLOCKER,
        "live_execution_claim": False,
        "external_verification_status": "NOT_EXECUTED",
    }


def main() -> int:
    value = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    print(json.dumps(verify_readiness_v2(value), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
