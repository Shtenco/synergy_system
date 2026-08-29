from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

EXPECTED_DIGEST = "b06425fdba3b69e1371c987714176d0435f90b511a7167abd13a4fb0a91476b8"
EXPECTED_PREVIOUS = "51566c3c87f21b1a22ddef9bb6aea6abd9170042790f37ac3ff559bf7ad89c60"
EXPECTED_CANONICAL_SURFACE = "0af8c4768129948cd773ed3f7bab5706a1d936a352d659c84d8d85468fa9edb8"
EXPECTED_CAPTURE_READINESS = "252fe1f12f326a6b31d18bb9b16f2bd31a8a72d12ad2053ae437864db8ef2eef"
EXPECTED_BLOCKERS = [
    "CANONICAL_MAIN_PROMOTION_NOT_EXECUTED",
    "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED",
    "EXTERNAL_HOST_MULTI_NODE_DEPLOYMENT_EXECUTION_NOT_CAPTURED",
]
NONE_AUTHORITIES = (
    "accounting_authority", "financial_authority", "payment_authority", "ai_authority",
    "signing_authority", "blockchain_submission_authority", "execution_authority",
)

class RC5VerificationError(ValueError):
    pass


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def verify_rc5(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != "synergy.economic-os-release-candidate/v5":
        raise RC5VerificationError("RC5 schema mismatch")
    item = dict(value)
    claimed = item.pop("digest", None)
    if claimed != EXPECTED_DIGEST or digest(item) != EXPECTED_DIGEST:
        raise RC5VerificationError("RC5 digest mismatch")
    if item.get("previous_release_digest") != EXPECTED_PREVIOUS:
        raise RC5VerificationError("previous RC mismatch")
    if item.get("canonicalization_surface_digest") != EXPECTED_CANONICAL_SURFACE:
        raise RC5VerificationError("canonicalization surface mismatch")
    if item.get("live_cycle_capture_readiness_digest") != EXPECTED_CAPTURE_READINESS:
        raise RC5VerificationError("capture readiness mismatch")
    if item.get("canonical_prs_mergeable_count") != 4 or item.get("canonical_prs_total") != 4:
        raise RC5VerificationError("canonical PR cardinality mismatch")
    if item.get("canonicalization_status") != "FOUR_MAIN_TARGET_CANONICAL_PRS_MERGEABLE_READY_NOT_MERGED":
        raise RC5VerificationError("canonicalization status drift")
    if item.get("live_cycle_capture_status") != "CAPTURE_PROTOCOL_READY_NO_LIVE_FIXTURE":
        raise RC5VerificationError("live capture status escalation")
    if item.get("protocol_status") != "E2E_PROTOCOL_DAG_CLOSED_NOT_LIVE_EXECUTED":
        raise RC5VerificationError("protocol live escalation")
    if item.get("economic_testnet_status") != "LOCAL_DISK_PERSISTENCE_RESTART_RECOVERY_VERIFIED_NOT_EXTERNAL_HOST_TESTNET":
        raise RC5VerificationError("testnet status escalation")
    if item.get("live_execution_claim") is not False or item.get("external_host_testnet_claim") is not False:
        raise RC5VerificationError("live/external host claim escalation")
    if item.get("release_status") != "ECONOMIC_OS_RC5_CANONICAL_AND_CAPTURE_READY_NOT_LIVE":
        raise RC5VerificationError("release status mismatch")
    if item.get("blockers") != EXPECTED_BLOCKERS:
        raise RC5VerificationError("blocker set mismatch")
    if any(item.get(name) != "NONE" for name in NONE_AUTHORITIES):
        raise RC5VerificationError("authority escalation")
    item["digest"] = claimed
    return item


def load_and_verify(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[1]
    value = json.loads((repo / "releases" / "economic_os_rc5_canonical_capture_ready_20260828.json").read_text(encoding="utf-8"))
    return verify_rc5(value)


if __name__ == "__main__":
    print(json.dumps(load_and_verify(), indent=2, sort_keys=True))
