from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_DIGEST = "03914c9199b25227026d02a2a2b2d0d8a11e958982c76865701729fff55710ba"
EXPECTED = {
    "schema": "synergy.ai-node-preproduction-release/v2",
    "release_id": "SYNERGY_AUTOPILOT_V5_AI_NODE_PREPRODUCTION_RC2_20260823",
    "node_id": "synergy-autopilot-v5-ai-node",
    "previous_preproduction_release_digest": "717b473fc67fbbdef89385d04b260ae2c8a8e85c75365ba8627785e1c8c271c7",
    "integration_manifest_digest": "a793250aaa2299fdaf1661e985423c2b62687a19395ceabcc7bb63c005defe54",
    "deployment_reference_v1_digest": "19375c02a286a4c14e704ad0496d1c6084ddb00e7c4bcf3506a304a6b0946b70",
    "system_registry_v2_digest": "12bdca330d81b81ec0acb32cf974f12fb36c5e72e6a1fea8680dc5e8470b275d",
    "ai_blockchain_deployment_commitment_v2_digest": "1b47ae40ae48848be1648da5cc1c443232a47dc59969e70a6dd033672e5397c0",
    "production_transition_gate_digest": "fd3f97c1422376ae507e7ec0ab1dcff529cba4ad9b5f6b1e9b7b62ef43d75b8c",
    "production_bootstrap_contract_digest": "605c6c953e998efb9585a88c1c8f1a022d7160e3448139c2b80a33e6b6cbabd3",
    "synergynet_artifact_sha256": "7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7",
    "synergynet_previous_location_evidence_digest": "c4102a8e668b79fc961a5f1767154154f4a600d320442770d74c7a006a5cee08",
    "synergynet_locator_availability_negative_evidence_digest": "2529d725e426c5028daab7346d1c704d643ffd209d35ceace7f7330203a6353f",
    "artifact_resolution_status": "BLOCKED_NEW_SYNERGYNET_DURABLE_LOCATOR_REQUIRED",
    "artifact_identity_status": "UNCHANGED_EXACT_REPRODUCIBLE",
    "lab_execution_status": "RUNNING_VERIFIED_THEN_STOPPED_GRACEFULLY",
    "current_running": False,
    "release_stage": "PREPRODUCTION_RC2_LOCATION_REMEDIATION_REQUIRED",
    "github_ci_status": "NOT_EXECUTED_UNKNOWN_STEPS_NULL",
    "production_requirements": [
        "NEW_SYNERGYNET_DURABLE_LOCATOR_AND_FRESH_SHA_SIZE_VERIFICATION",
        "NEW_PERSISTENT_PRODUCTION_HOST_PROFILE",
        "NEW_PRODUCTION_SUPERVISOR_CONFIG",
        "FRESH_HEALTH_AND_TRANSPORT_ROUNDTRIP",
        "FRESH_PRODUCTION_DEPLOYMENT_EVIDENCE",
        "FRESH_PRODUCTION_DEPLOYMENT_RESULT",
        "EXPLICIT_GOVERNANCE_PROMOTION",
    ],
    "auto_start": False,
    "financial_authority": "NONE",
    "payment_authority": "NONE",
    "accounting_authority": "NONE",
    "blockchain_submission_authority": "NONE",
    "execution_authority": "NONE",
}


class PreProductionRC2Error(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def verify(value: dict[str, Any]) -> str:
    if not isinstance(value, dict):
        raise PreProductionRC2Error("release must be object")
    payload = dict(value)
    claimed = payload.pop("release_manifest_digest", None)
    actual = hashlib.sha256(canonical(payload)).hexdigest()
    if claimed != EXPECTED_DIGEST or actual != EXPECTED_DIGEST:
        raise PreProductionRC2Error("release digest mismatch")
    if payload != EXPECTED:
        raise PreProductionRC2Error("release identity/state/authority mismatch")
    return actual


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "releases" / "synergy_autopilot_v5_ai_node_preproduction_rc2.json"
    digest = verify(json.loads(path.read_text(encoding="utf-8")))
    print(json.dumps({"status": "PASS", "release_manifest_digest": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
