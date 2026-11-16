from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

EXPECTED_DIGEST = "51566c3c87f21b1a22ddef9bb6aea6abd9170042790f37ac3ff559bf7ad89c60"
EXPECTED_PREVIOUS = "bb5493ff92f0f77a10c40b93b474bef324d0c75fb44c4630d27fdee9932acd26"
EXPECTED_PERSISTENCE_EVIDENCE = "7c533e6ebb3b3177ef9191d1951c930ddd9d6f49541b0fa3982924f2dce86680"
EXPECTED_BLOCKERS = [
    "STACKED_PR_CHAIN_NOT_CANONICALLY_MERGED",
    "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED",
    "EXTERNAL_HOST_MULTI_NODE_DEPLOYMENT_EXECUTION_NOT_CAPTURED",
]
NONE_AUTHORITIES = (
    "accounting_authority", "financial_authority", "payment_authority",
    "ai_authority", "signing_authority", "blockchain_submission_authority",
    "execution_authority",
)


class RC4VerificationError(ValueError):
    pass


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def verify_rc4(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != "synergy.economic-os-release-candidate/v4":
        raise RC4VerificationError("RC4 schema mismatch")
    item = dict(value)
    claimed = item.pop("digest", None)
    if claimed != EXPECTED_DIGEST or digest(item) != EXPECTED_DIGEST:
        raise RC4VerificationError("RC4 digest mismatch")
    if item.get("previous_release_digest") != EXPECTED_PREVIOUS:
        raise RC4VerificationError("previous RC mismatch")
    if item.get("testnet_persistent_restart_execution_evidence_digest") != EXPECTED_PERSISTENCE_EVIDENCE:
        raise RC4VerificationError("persistence evidence mismatch")
    if item.get("economic_testnet_status") != "LOCAL_DISK_PERSISTENCE_RESTART_RECOVERY_VERIFIED_NOT_EXTERNAL_HOST_TESTNET":
        raise RC4VerificationError("testnet status escalation/drift")
    if item.get("protocol_status") != "E2E_PROTOCOL_DAG_CLOSED_NOT_LIVE_EXECUTED":
        raise RC4VerificationError("protocol live-execution escalation")
    if item.get("economic_blockchain_commitment_status") != "CREATED_NOT_SUBMITTED":
        raise RC4VerificationError("blockchain submission escalation")
    if item.get("canonical_merge_status") != "STACKED_PR_CANDIDATE_NOT_MERGED":
        raise RC4VerificationError("canonical merge escalation")
    if item.get("live_execution_claim") is not False or item.get("external_host_testnet_claim") is not False:
        raise RC4VerificationError("live/external-host claim escalation")
    if item.get("blockers") != EXPECTED_BLOCKERS:
        raise RC4VerificationError("blocker set mismatch")
    if any(item.get(name) != "NONE" for name in NONE_AUTHORITIES):
        raise RC4VerificationError("authority escalation")
    item["digest"] = claimed
    return item


def load_and_verify(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[1]
    value = json.loads((repo / "releases" / "economic_os_rc4_local_persistence_restart_20260828.json").read_text(encoding="utf-8"))
    return verify_rc4(value)


if __name__ == "__main__":
    print(json.dumps(load_and_verify(), indent=2, sort_keys=True))
