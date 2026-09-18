from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "federation_v5.py"
CATALOG = ROOT / "config" / "repository_catalog_v5.json"
REQ_SCHEMA = ROOT / "config" / "capability-envelope-v2.schema.json"
RES_SCHEMA = ROOT / "config" / "capability-result-v2.schema.json"
REGISTRY = ROOT / "config" / "capability_registry_v2.json"

REQUEST_FIELDS = {
    "protocol","request_id","source_principal","target_principal","capability",
    "input","constraints","approval_context","idempotency_key","trace_id",
}
RESULT_FIELDS = {
    "protocol","request_id","provider","capability","status","result_objects",
    "evidence","usage","cost","trace_id","authority_statement",
}
STATUSES = {"ACCEPTED","REJECTED","RUNNING","COMPLETED","FAILED"}


class CapabilityRegistryV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("federation_v5", MODULE)
        cls.mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.mod)

    def test_v2_schemas_exist_with_closed_contract(self):
        req = json.loads(REQ_SCHEMA.read_text(encoding="utf-8"))
        res = json.loads(RES_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(req["required"]), REQUEST_FIELDS)
        self.assertEqual(set(res["required"]), RESULT_FIELDS)
        self.assertEqual(req["properties"]["protocol"]["const"], "synergy.capability.v2")
        self.assertEqual(res["properties"]["protocol"]["const"], "synergy.capability-result.v2")
        self.assertEqual(set(res["properties"]["status"]["enum"]), STATUSES)

    def test_registry_is_deterministic_projection_of_catalog(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        expected = self.mod.build_capability_registry(catalog)
        actual = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_known_capability_owners(self):
        d = json.loads(REGISTRY.read_text(encoding="utf-8"))
        by = {x["capability"]: x for x in d["capabilities"]}
        self.assertEqual(by["accounting.snapshot"]["canonical_provider"], "synergy_financial_os")
        self.assertEqual(by["payment.route"]["canonical_provider"], "synergy_pay_system")
        self.assertEqual(by["trading.propose_portfolio"]["canonical_provider"], "midas_ai")
        self.assertEqual(by["science.build_evidence_package"]["canonical_provider"], "nexus_science_agent")
        self.assertEqual(by["business.execute_approved_task"]["canonical_provider"], "agi_autopilot")

    def test_duplicate_provider_is_rejected(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        other = next(x for x in catalog["repositories"] if x["name"] != "midas_ai")
        other["capabilities_provided"].append("trading.propose_portfolio")
        with self.assertRaisesRegex(ValueError, "E_CAPABILITY_AMBIGUOUS"):
            self.mod.build_capability_registry(catalog)


if __name__ == "__main__":
    unittest.main()
