import copy, hashlib, json, unittest
from pathlib import Path
from scripts.verify_autopilot_ai_node_preproduction_rc5 import verify, RC5Error, canonical

ROOT = Path(__file__).resolve().parents[1]

class RC5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads((ROOT/"releases"/"synergy_autopilot_v5_ai_node_preproduction_rc5.json").read_text(encoding="utf-8"))

    def test_canonical(self):
        self.assertEqual(verify(self.value), "0dd56320df6a1e18a7f77470b0609f55cb9c134ac67bbedeebdd3600e724124b")

    def test_reject_current_lineage_substitution_with_fresh_hash(self):
        for field in (
            "deployment_reference_v2_digest",
            "synergynet_location_evidence_v3_digest",
            "synergynet_transport_binding_v2_digest",
            "meta_os_profile_v3_digest",
            "meta_os_admission_v3_digest",
            "production_bootstrap_v4_digest",
            "ai_blockchain_preproduction_commitment_v3_digest",
            "federation_registry_v3_digest",
        ):
            c = copy.deepcopy(self.value); c[field] = "0"*64
            p = dict(c); p.pop("release_manifest_digest", None)
            c["release_manifest_digest"] = hashlib.sha256(canonical(p)).hexdigest()
            with self.subTest(field=field), self.assertRaises(RC5Error): verify(c)

    def test_reject_running_or_authority_escalation(self):
        for field, value in (
            ("current_running", True), ("auto_start", True), ("nexus_network_access", "FULL"),
            ("financial_authority", "ROOT"), ("payment_authority", "ROOT"),
            ("accounting_authority", "ROOT"), ("host_execution_authority", "ROOT"),
            ("blockchain_submission_authority", "ROOT"), ("execution_authority", "ROOT"),
        ):
            c = copy.deepcopy(self.value); c[field] = value
            p = dict(c); p.pop("release_manifest_digest", None)
            c["release_manifest_digest"] = hashlib.sha256(canonical(p)).hexdigest()
            with self.subTest(field=field), self.assertRaises(RC5Error): verify(c)

if __name__ == "__main__": unittest.main()
