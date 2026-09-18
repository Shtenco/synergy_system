from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"config"/"exchange_object_registry_v1.json"
EXPECTED={
 "DemandSignal","ResourceState","TechnologyCandidate","ProjectProposal",
 "CapitalAuthorization","PaymentIntent","SettlementReceipt","EvidencePackage","AccountingSnapshot"
}

class ExchangeObjectRegistryTests(unittest.TestCase):
    def load(self):
        return json.loads(REG.read_text(encoding="utf-8"))

    def test_exact_object_vocabulary(self):
        d=self.load()
        self.assertEqual(d["schema"],"synergy.exchange-object-registry/v1")
        self.assertEqual({x["name"] for x in d["objects"]},EXPECTED)

    def test_semantic_authority_boundaries(self):
        by={x["name"]:x for x in self.load()["objects"]}
        self.assertEqual(by["CapitalAuthorization"]["semantic_owner"],"synergy_financial_os")
        self.assertEqual(by["PaymentIntent"]["semantic_owner"],"synergy_financial_os")
        self.assertEqual(by["SettlementReceipt"]["semantic_owner"],"synergy_pay_system")
        self.assertEqual(by["AccountingSnapshot"]["semantic_owner"],"synergy_financial_os")
        self.assertEqual(by["ProjectProposal"]["semantic_owner"],"synergy_eurasian")
        self.assertTrue(all(x["federation_owner"]=="synergy_system" for x in by.values()))

    def test_existing_eurasian_objects_keep_provenance(self):
        by={x["name"]:x for x in self.load()["objects"]}
        for name in ("DemandSignal","ResourceState","TechnologyCandidate","ProjectProposal","EvidencePackage"):
            self.assertIn("Shtenco/synergy_eurasian",by[name]["provenance"])

    def test_missing_objects_have_local_contract_schemas(self):
        by={x["name"]:x for x in self.load()["objects"]}
        for name in ("CapitalAuthorization","PaymentIntent","SettlementReceipt","AccountingSnapshot"):
            ref=by[name]["schema_ref"]
            self.assertTrue((ROOT/ref).exists(),f"{name}: {ref}")

if __name__=="__main__":
    unittest.main()
