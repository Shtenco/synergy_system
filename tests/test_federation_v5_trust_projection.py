from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"scripts"/"generate_federation_v5.py"
CAT=ROOT/"config"/"repository_catalog_v5.json"
EXPECTED_AUTO_ROUTES={
 "autopilot.submit","autopilot.status","autopilot.approve","autopilot.execute",
 "autopilot.capabilities","nexus.runtime","nexus.memory.search","nexus.memory.upsert",
}

class FederationV5TrustProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location("generate_federation_v5",GEN)
        cls.mod=importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.mod)
        cls.catalog=json.loads(CAT.read_text(encoding="utf-8"))

    def test_only_explicitly_trusted_members_are_projected(self):
        trust=self.mod.build_trust_source(self.catalog)
        projected={x["name"] for x in trust["repositories"]}
        projected|={x["name"] for x in trust["control_principals"]}
        expected={
            r["name"] for r in self.catalog["repositories"]
            if r["trust_enabled"] and r["federation_membership"]
        }
        self.assertEqual(projected,expected)
        self.assertNotIn("synergy_agi_trader",projected)
        for r in self.catalog["repositories"]:
            if r["lifecycle_status"] in {"LEGACY","ARCHIVE"}:
                self.assertNotIn(r["name"],projected)

    def test_auto_company_is_separate_allowlisted_control_principal(self):
        trust=self.mod.build_trust_source(self.catalog)
        self.assertEqual(len(trust["control_principals"]),1)
        c=trust["control_principals"][0]
        self.assertEqual(c["name"],"synergy_ai_company")
        self.assertEqual(c["capability_policy"],"ALLOWLIST")
        self.assertEqual(set(c["rpc_allow"]),EXPECTED_AUTO_ROUTES)
        self.assertNotIn("synergy_ai_company",{x["name"] for x in trust["repositories"]})

    def test_ordinary_repository_callers_remain_deny_by_default(self):
        trust=self.mod.build_trust_source(self.catalog)
        self.assertTrue(trust["repositories"])
        for r in trust["repositories"]:
            self.assertEqual(r["capability_policy"],"DENY",r["name"])
            self.assertEqual(r["rpc_allow"],[],r["name"])

    def test_trust_source_is_bound_to_catalog_digest(self):
        trust=self.mod.build_trust_source(self.catalog)
        digest=trust["catalog_digest"]
        self.assertTrue(digest)
        for item in trust["repositories"]+trust["control_principals"]:
            self.assertEqual(item["catalog_digest"],digest)

if __name__=="__main__":
    unittest.main()
