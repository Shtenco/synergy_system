import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_autopilot_ai_node_preproduction_rc1 import PreProductionReleaseError, verify_release  # noqa: E402


class PreProductionRC1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = json.loads((ROOT / "releases" / "synergy_autopilot_v5_ai_node_preproduction_rc1.json").read_text(encoding="utf-8"))

    def test_canonical_release(self):
        self.assertEqual(
            verify_release(self.release),
            "717b473fc67fbbdef89385d04b260ae2c8a8e85c75365ba8627785e1c8c271c7",
        )

    def reject(self, field, value):
        candidate = copy.deepcopy(self.release)
        candidate[field] = value
        candidate["release_manifest_digest"] = "0" * 64
        with self.assertRaises(PreProductionReleaseError):
            verify_release(candidate)

    def test_reject_deployment_reference_substitution(self):
        self.reject("deployment_reference_v1_digest", "f" * 64)

    def test_reject_registry_substitution(self):
        self.reject("system_registry_v2_digest", "f" * 64)

    def test_reject_production_gate_substitution(self):
        self.reject("production_transition_gate_digest", "f" * 64)

    def test_reject_current_running(self):
        self.reject("current_running", True)

    def test_reject_production_stage(self):
        self.reject("release_stage", "PRODUCTION")

    def test_reject_ci_green_without_evidence(self):
        self.reject("github_ci_status", "PASS")

    def test_reject_erased_production_requirements(self):
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
