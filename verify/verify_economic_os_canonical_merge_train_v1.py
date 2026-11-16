from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_DIGEST = "ce8ea7aa41acdf08e2995ba1edec4167449de69f1ce0791afa249195f3a8aed6"
EXPECTED_FINANCIAL_PRS = [26, 27, 28, 29, 30, 31, 32]
EXPECTED_METAPAY_PRS = [13, 14]
EXPECTED_UNKNOWN_SCOPES = {
    "METAPAY_REVERSAL_V2",
    "FINANCIAL_REVERSAL_ACCOUNTING_V2",
    "FINANCIAL_BUDGET_STATE_V3",
    "FINANCIAL_AVAILABLE_CAPACITY_V4",
    "SYSTEM_ECONOMIC_CYCLE_V1",
    "BLOCKCHAIN_ECONOMIC_COMMITMENT_V1",
    "ECONOMIC_TESTNET_V1",
    "ECONOMIC_OS_RC1",
}

class MergeTrainV1Error(ValueError):
    pass

def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def verify(value: dict[str, Any]) -> str:
    if not isinstance(value, dict):
        raise MergeTrainV1Error("merge train must be object")
    body = dict(value); claimed = body.pop("digest", None)
    actual = hashlib.sha256(canonical(body)).hexdigest()
    if claimed != EXPECTED_DIGEST or actual != EXPECTED_DIGEST:
        raise MergeTrainV1Error("merge train digest mismatch")
    if body.get("schema") != "synergy.economic-os-canonical-merge-train/v1":
        raise MergeTrainV1Error("merge train schema mismatch")
    if body.get("promotion_policy") != "NO_CANONICAL_MERGE_OR_STATUS_PROMOTION_WITHOUT_EXECUTED_PASS_EVIDENCE":
        raise MergeTrainV1Error("promotion policy drift")
    if body.get("financial_os_lane", {}).get("ordered_prs") != EXPECTED_FINANCIAL_PRS:
        raise MergeTrainV1Error("Financial OS order mismatch")
    if body.get("metapay_lane", {}).get("ordered_prs") != EXPECTED_METAPAY_PRS:
        raise MergeTrainV1Error("MetaPay order mismatch")
    evidence = body.get("observed_ci_evidence")
    if not isinstance(evidence, list) or {x.get("scope") for x in evidence} != EXPECTED_UNKNOWN_SCOPES:
        raise MergeTrainV1Error("CI evidence set mismatch")
    for row in evidence:
        if row.get("steps_state") != "NULL" or row.get("logs_state") != "NULL" or row.get("classification") != "NOT_EXECUTED_UNKNOWN":
            raise MergeTrainV1Error("CI evidence may not be promoted without a new evidence generation")
    if body.get("current_gate") != "BLOCKED_GITHUB_ACTIONS_NO_STEP_EXECUTION_EVIDENCE":
        raise MergeTrainV1Error("merge gate removed")
    if body.get("merge_authority") != "HUMAN_MAINTAINER_ONLY" or body.get("auto_merge") is not False or body.get("ai_merge_authority") != "NONE":
        raise MergeTrainV1Error("merge authority escalation")
    return actual

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    value = json.loads((root / "release_trains" / "economic_os_canonical_merge_train_v1.json").read_text(encoding="utf-8"))
    print(json.dumps({"status":"PASS","digest":verify(value)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
