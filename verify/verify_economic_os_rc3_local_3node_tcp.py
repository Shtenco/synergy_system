from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "synergy.economic-os-release-candidate/v3"
EXPECTED_DIGEST = "bb5493ff92f0f77a10c40b93b474bef324d0c75fb44c4630d27fdee9932acd26"
EXPECTED_PREVIOUS = "6f208af699c1ab26b69e6525a3b48cd5fa62dc066419423dd518dfe163e4fe24"
EXPECTED_LOOPBACK = "6f80d6cfdbce8eb0b2410c7e440f260eaf6199da8e5b64ce48c365c68be684d5"
EXPECTED_BLOCKERS = [
    "STACKED_PR_CHAIN_NOT_CANONICALLY_MERGED",
    "ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED",
    "PERSISTENT_EXTERNAL_HOST_MULTI_NODE_TESTNET_EXECUTION_NOT_CAPTURED",
]


class EconomicOSRC3Error(ValueError):
    pass


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def verify_rc3(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != SCHEMA:
        raise EconomicOSRC3Error("unsupported RC3 schema")
    item = dict(value)
    claimed = item.pop("digest", None)
    if not isinstance(claimed, str) or digest(item) != claimed or claimed != EXPECTED_DIGEST:
        raise EconomicOSRC3Error("RC3 digest mismatch")
    exact = {
        "release_id": "SYNERGY_ECONOMIC_OS_RC3_LOCAL_3NODE_TCP_20260828",
        "previous_release_digest": EXPECTED_PREVIOUS,
        "economic_cycle_digest": "83f9c3ee0c168ca50212ebaa1e64c58c08eb87fd040a8b5f214ee4987242f3f1",
        "economic_commitment_digest": "9ffd71e7f535ff91cd4cedfb229ac0b43972bc8a2e82f8dce269b7440a9e65a8",
        "testnet_genesis_digest": "cfba3627eb65d933ed1dec416bfe1c28ecf586312028efc7e629859f315678b2",
        "testnet_local_execution_evidence_digest": "a841d4a662feca85ad459ce2da157279d7a754280dfb75aa1ef025f92c7f1268",
        "testnet_loopback_execution_evidence_digest": EXPECTED_LOOPBACK,
        "testnet_loopback_evidence_source_commit": "409b323b622500f2fb6bfe22260d23364cf7305a",
        "financial_os_terminal_commit": "d21ce6b5bd91422c45f938b2d4ec641974106944",
        "metapay_terminal_commit": "a4b7b2876915e7f70089947a5b40f3cff81458d9",
        "compute_preproduction_rc5_digest": "0dd56320df6a1e18a7f77470b0609f55cb9c134ac67bbedeebdd3600e724124b",
        "compute_production_bootstrap_v5_digest": "6ccecccc03189c6de934abf146cab87bb25b022551ba8d453cfefd4f5a3cdffd",
        "protocol_status": "E2E_PROTOCOL_DAG_CLOSED_NOT_LIVE_EXECUTED",
        "economic_blockchain_commitment_status": "CREATED_NOT_SUBMITTED",
        "economic_testnet_status": "LOCAL_3_NODE_TCP_PROPAGATION_VERIFIED_NOT_PERSISTENT_EXTERNAL_TESTNET",
        "canonical_merge_status": "STACKED_PR_CANDIDATE_NOT_MERGED",
        "live_execution_claim": False,
        "persistent_external_testnet_claim": False,
        "release_status": "ECONOMIC_OS_RC3_LOCAL_3NODE_TCP_VERIFIED_NOT_PERSISTENT_EXTERNAL",
    }
    for field, expected in exact.items():
        if item.get(field) != expected:
            raise EconomicOSRC3Error(f"RC3 mismatch: {field}")
    if item.get("blockers") != EXPECTED_BLOCKERS:
        raise EconomicOSRC3Error("RC3 blocker set mismatch")
    for authority in (
        "accounting_authority", "financial_authority", "payment_authority", "ai_authority",
        "signing_authority", "blockchain_submission_authority", "execution_authority",
    ):
        if item.get(authority) != "NONE":
            raise EconomicOSRC3Error(f"RC3 authority escalation: {authority}")
    item["digest"] = claimed
    return item


def load_rc3(root: Path | None = None) -> dict[str, Any]:
    repo_root = root or Path(__file__).resolve().parents[1]
    return json.loads((repo_root / "releases" / "economic_os_rc3_local_3node_tcp_20260828.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    print(verify_rc3(load_rc3())["digest"])
