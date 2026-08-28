from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_DIGEST = "060458d94b82afc4ce944b780e547dcd67c68499b0068eaeb2906446f4505913"
EXPECTED_CYCLE = "83f9c3ee0c168ca50212ebaa1e64c58c08eb87fd040a8b5f214ee4987242f3f1"
EXPECTED_COMMITMENT = "9ffd71e7f535ff91cd4cedfb229ac0b43972bc8a2e82f8dce269b7440a9e65a8"
EXPECTED_GENESIS = "cfba3627eb65d933ed1dec416bfe1c28ecf586312028efc7e629859f315678b2"
EXPECTED_BLOCKERS = [
    "STACKED_PR_CHAIN_NOT_CANONICALLY_MERGED",
    "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED",
    "ECONOMIC_TESTNET_EXECUTION_EVIDENCE_NOT_CAPTURED",
]


class EconomicOSRC1Error(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def verify(value: dict[str, Any]) -> str:
    if not isinstance(value, dict):
        raise EconomicOSRC1Error("release must be object")
    body = dict(value)
    claimed = body.pop("digest", None)
    actual = hashlib.sha256(canonical(body)).hexdigest()
    if claimed != EXPECTED_DIGEST or actual != EXPECTED_DIGEST:
        raise EconomicOSRC1Error("release digest mismatch")
    if body.get("schema") != "synergy.economic-os-release-candidate/v1":
        raise EconomicOSRC1Error("release schema mismatch")
    if body.get("economic_cycle_digest") != EXPECTED_CYCLE:
        raise EconomicOSRC1Error("economic cycle root mismatch")
    if body.get("economic_commitment_digest") != EXPECTED_COMMITMENT:
        raise EconomicOSRC1Error("economic commitment root mismatch")
    if body.get("testnet_genesis_digest") != EXPECTED_GENESIS:
        raise EconomicOSRC1Error("testnet genesis root mismatch")
    if body.get("protocol_status") != "E2E_PROTOCOL_DAG_CLOSED_NOT_LIVE_EXECUTED":
        raise EconomicOSRC1Error("protocol status escalation")
    if body.get("economic_blockchain_commitment_status") != "CREATED_NOT_SUBMITTED":
        raise EconomicOSRC1Error("blockchain commitment status mismatch")
    if body.get("economic_testnet_status") != "READY_NOT_EXECUTED":
        raise EconomicOSRC1Error("testnet status escalation")
    if body.get("canonical_merge_status") != "STACKED_PR_CANDIDATE_NOT_MERGED":
        raise EconomicOSRC1Error("canonical merge claim mismatch")
    if body.get("live_execution_claim") is not False:
        raise EconomicOSRC1Error("live execution claim forbidden")
    if body.get("release_status") != "ECONOMIC_OS_RC1_TESTNET_READY_NOT_EXECUTED":
        raise EconomicOSRC1Error("release status mismatch")
    if body.get("blockers") != EXPECTED_BLOCKERS:
        raise EconomicOSRC1Error("release blockers mismatch")
    for authority in (
        "accounting_authority", "financial_authority", "payment_authority", "ai_authority",
        "signing_authority", "blockchain_submission_authority", "execution_authority",
    ):
        if body.get(authority) != "NONE":
            raise EconomicOSRC1Error(f"{authority} escalation")
    return actual


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    value = json.loads((root / "releases" / "economic_os_rc1_testnet_ready_20260828.json").read_text(encoding="utf-8"))
    digest = verify(value)
    print(json.dumps({"status": "PASS", "digest": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
