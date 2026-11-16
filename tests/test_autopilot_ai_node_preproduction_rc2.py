import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_autopilot_ai_node_preproduction_rc2 import PreProductionRC2Error, verify  # noqa: E402


class PreProductionRC2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = json.loads((ROOT / "releases" / "synergy_autopilot_v5_ai_node_preproduction_rc2.json").read_text(encoding="utf-8"))

    def test_canonical_rc2(self):
        self.assertEqual(
            verify(self.release),
            "03914c9199b25227026d02a2a2b2d0d8a11e958982c76865701729fff55710ba",
        )

    def reject(self, field, value):
        candidate = copy.deepcopy(self.release)
        candidate[field] = value
        candidate["release_manifest_digest"] = "0" * 64
        with self.assertRaises(PreProductionRC2Error):
            verify(candidate)

    def test_reject_locator_negative_evidence_erasure(self):
        self.reject("synergynet_locator_availability_negative_evidence_digest", "f" * 64)

    def test_reject_false_resolved_locator(self):
        self.reject("artifact_resolution_status", "RESOLVED")

    def test_reject_artifact_identity_change(self):
        self.reject("artifact_identity_status", "UNKNOWN")

    def test_reject_production_stage(self):
        self.reject("release_stage", "PRODUCTION")

    def test_reject_current_running(self):
        self.reject("current_running", True)

    def test_reject_ci_pass_without_steps(self):
        self.reject("github_ci_status", "PASS")

    def test_reject_requirement_erasure(self):
        self.reject("production_requirements", [])

    def test_reject_authority_escalation(self):
        for field in (
            "financial_authority",
            "payment_authority",
            "accounting_authority",
            "blockchain_submission_authority",
            "execution_authority",
        ):
            with self.subTest(field=field):
                self.reject(field, "ROOT")


if __name__ == "__main__":
    unittest.main()
