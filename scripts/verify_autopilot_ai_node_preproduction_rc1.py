from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_DIGEST = "717b473fc67fbbdef89385d04b260ae2c8a8e85c75365ba8627785e1c8c271c7"
EXPECTED = {
    "schema": "synergy.ai-node-preproduction-release/v1",
    "release_id": "SYNERGY_AUTOPILOT_V5_AI_NODE_PREPRODUCTION_RC1_20260823",
    "node_id": "synergy-autopilot-v5-ai-node",
    "canonical_owner_repository": "Shtenco/agi_autopilot",
    "base_system": "AUTOPILOT_V5",
    "integration_manifest_digest": "a793250aaa2299fdaf1661e985423c2b62687a19395ceabcc7bb63c005defe54",
    "release_roots_digest": "224e6c43bfccb3b0db7acf92f243dace0ee5228a7ab31a0be140328e692f3630",
    "deployment_reference_v1_digest": "19375c02a286a4c14e704ad0496d1c6084ddb00e7c4bcf3506a304a6b0946b70",
    "system_registry_v2_digest": "12bdca330d81b81ec0acb32cf974f12fb36c5e72e6a1fea8680dc5e8470b275d",
    "synergynet_transport_binding_digest": "3c8198e10863c52c0492ca422c404a1e05e6fd2f48f4c393587d9d87eee3855f",
    "meta_os_admission_v2_digest": "4d3502dba28745b8a734c082ca0260cbbfd4ead11a1396537434844df9987ee3",
    "lab_deployment_result_digest": "011c3ce24cfd33dc99fbdea0ea2f5dcd344deefd927f57c1b9c1fa3e3eaa3833",
    "ai_blockchain_deployment_commitment_v2_digest": "1b47ae40ae48848be1648da5cc1c443232a47dc59969e70a6dd033672e5397c0",
    "production_transition_gate_digest": "fd3f97c1422376ae507e7ec0ab1dcff529cba4ad9b5f6b1e9b7b62ef43d75b8c",
    "release_archive_sha256": "afba4eb7508564292f6695dbef69e9a043a998da8a2e4b587922c17bbefb37cb",
    "release_archive_size": 1045560,
    "nexus_artifact_sha256": "e87d00809ff976c76655b892166ec1cf1f13a893927ead156295b6814fcd9325",
    "synergynet_artifact_sha256": "7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7",
    "lab_execution_status": "RUNNING_VERIFIED_THEN_STOPPED_GRACEFULLY",
    "current_running": False,
    "release_stage": "PREPRODUCTION_RC1_NOT_PRODUCTION",
    "github_ci_status": "NOT_EXECUTED_UNKNOWN_STEPS_NULL",
    "github_ci_runs": {
        "agi_autopilot": 32663893360,
        "synergynet": 32659267387,
        "synergy_meta_os": 32659914040,
        "synergy_system": 32660087936,
        "synergy_ai_blockchain": 32660181014,
    },
    "production_requirements": [
        "NEW_PERSISTENT_PRODUCTION_HOST_PROFILE",
        "NEW_PRODUCTION_SUPERVISOR_CONFIG",
        "FRESH_ARTIFACT_RESOLUTION_AND_HASH_VERIFICATION",
        "FRESH_PRODUCTION_HEALTH_AND_TRANSPORT_ROUNDTRIP",
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


class PreProductionReleaseError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def verify_release(value: dict[str, Any]) -> str:
    if not isinstance(value, dict):
        raise PreProductionReleaseError("release must be object")
    if set(value) != set(EXPECTED) | {"release_manifest_digest"}:
        raise PreProductionReleaseError("unexpected field set")
    payload = dict(value)
    claimed = payload.pop("release_manifest_digest")
    if payload != EXPECTED:
        raise PreProductionReleaseError("release identity/state/authority mismatch")
    actual = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    if actual != EXPECTED_DIGEST or claimed != actual:
        raise PreProductionReleaseError("release manifest digest mismatch")
    return actual


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "releases" / "synergy_autopilot_v5_ai_node_preproduction_rc1.json").read_text(encoding="utf-8"))
    digest = verify_release(data)
    print(json.dumps({"status": "PASS", "release_manifest_digest": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
