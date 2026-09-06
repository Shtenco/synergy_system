import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_all_flow_steps_are_registered_contract_types():
    contracts = json.loads((ROOT / "config" / "contract_registry_v1.json").read_text(encoding="utf-8"))
    flows = json.loads((ROOT / "config" / "flow_registry_v1.json").read_text(encoding="utf-8"))
    known = {entry["type"] for entry in contracts["contracts"]}
    for flow in flows["flows"]:
        assert flow["steps"], f"flow {flow['flow_id']} must not be empty"
        assert all(step in known for step in flow["steps"]), f"unknown step in {flow['flow_id']}"


def test_flows_have_unique_ids_and_no_duplicate_steps():
    flows = json.loads((ROOT / "config" / "flow_registry_v1.json").read_text(encoding="utf-8"))["flows"]
    ids = [flow["flow_id"] for flow in flows]
    assert len(ids) == len(set(ids))
    for flow in flows:
        assert len(flow["steps"]) == len(set(flow["steps"]))


def test_global_causation_and_authority_invariants_are_enabled():
    global_invariants = json.loads((ROOT / "config" / "flow_registry_v1.json").read_text(encoding="utf-8"))["global_invariants"]
    assert global_invariants["same_correlation_id_within_flow"] is True
    assert global_invariants["strict_previous_contract_causation"] is True
    assert global_invariants["authority_registry_enforced"] is True
    assert global_invariants["payload_hash_required"] is True
