from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "repository_catalog_v5.json"
SCHEMA = ROOT / "config" / "repository_catalog_v5.schema.json"

LIFECYCLE = {"CANONICAL", "CANDIDATE", "R&D", "LEGACY", "ARCHIVE"}
AUTHORITY_KEYS = {
    "execution", "financial", "accounting", "payment", "settlement",
    "blockchain_submission", "code_write", "external_side_effect",
}


class RepositoryCatalogV5Tests(unittest.TestCase):
    def load(self):
        self.assertTrue(CATALOG.exists(), "V5 catalog must exist")
        self.assertTrue(SCHEMA.exists(), "V5 catalog schema must exist")
        return json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_catalog_has_dynamic_repository_set(self):
        d = self.load()
        self.assertEqual(d["schema"], "synergy.repository-catalog/v5")
        self.assertNotIn("repository_count", d, "count must be derived, never authoritative")
        repos = d["repositories"]
        self.assertGreater(len(repos), 0)
        self.assertEqual(len({r["name"] for r in repos}), len(repos))
        self.assertEqual(len({str(r["github_id"]) for r in repos}), len(repos))
        self.assertEqual(len({r["repo_url"] for r in repos}), len(repos))

    def test_every_repository_has_closed_status_and_policy_fields(self):
        for r in self.load()["repositories"]:
            self.assertIn(r["lifecycle_status"], LIFECYCLE, r["name"])
            self.assertEqual(set(r["authority"]), AUTHORITY_KEYS, r["name"])
            for key in (
                "system_kind", "domain", "role", "risk_class",
                "federation_membership", "trust_enabled",
                "capabilities_provided", "capabilities_consumed",
                "allowed_exchange_objects", "canonical_successor",
                "provenance_sources", "verification",
            ):
                self.assertIn(key, r, f"{r['name']} missing {key}")

    def test_archive_and_legacy_are_not_implicitly_trusted(self):
        for r in self.load()["repositories"]:
            if r["lifecycle_status"] == "ARCHIVE":
                self.assertFalse(r["trust_enabled"], r["name"])
                self.assertFalse(r["federation_membership"], r["name"])
            if r["lifecycle_status"] == "LEGACY":
                self.assertFalse(r["trust_enabled"], r["name"])

    def test_rnd_has_no_canonical_economic_authority(self):
        forbidden = {"financial", "accounting", "payment", "settlement"}
        for r in self.load()["repositories"]:
            if r["lifecycle_status"] == "R&D":
                for key in forbidden:
                    self.assertEqual(r["authority"][key], "NONE", f"{r['name']}:{key}")

    def test_known_governance_boundaries(self):
        by_name = {r["name"]: r for r in self.load()["repositories"]}
        self.assertEqual(by_name["synergy_financial_os"]["authority"]["accounting"], "CANONICAL")
        self.assertEqual(by_name["synergy_pay_system"]["authority"]["settlement"], "CANONICAL")
        self.assertEqual(by_name["midas_ai"]["authority"]["execution"], "NONE")
        self.assertEqual(by_name["synergy_agi_trader"]["lifecycle_status"], "R&D")
        self.assertFalse(by_name["synergy_agi_trader"]["trust_enabled"])


if __name__ == "__main__":
    unittest.main()
