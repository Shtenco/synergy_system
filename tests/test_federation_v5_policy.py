from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "federation_v5.py"
CATALOG = ROOT / "config" / "repository_catalog_v5.json"


class FederationV5PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not MODULE.exists():
            cls.mod = None
            return
        spec = importlib.util.spec_from_file_location("federation_v5", MODULE)
        cls.mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.mod)

    def load_catalog(self):
        return json.loads(CATALOG.read_text(encoding="utf-8"))

    def assertRule(self, catalog, prefix):
        self.assertIsNotNone(self.mod, "scripts/federation_v5.py must exist")
        errors = self.mod.validate_catalog(catalog)
        self.assertTrue(any(e.startswith(prefix) for e in errors), errors)

    def test_module_exists_and_live_catalog_is_valid(self):
        self.assertIsNotNone(self.mod, "scripts/federation_v5.py must exist")
        self.assertEqual(self.mod.validate_catalog(self.load_catalog()), [])

    def test_duplicate_repository_name_rejected(self):
        d = self.load_catalog()
        d["repositories"].append(copy.deepcopy(d["repositories"][0]))
        self.assertRule(d, "E_DUPLICATE_NAME:")

    def test_archive_trust_rejected(self):
        d = self.load_catalog()
        r = next(x for x in d["repositories"] if x["lifecycle_status"] == "ARCHIVE")
        r["trust_enabled"] = True
        self.assertRule(d, "E_ARCHIVE_TRUST:")

    def test_rnd_economic_authority_rejected(self):
        d = self.load_catalog()
        r = next(x for x in d["repositories"] if x["lifecycle_status"] == "R&D")
        r["authority"]["accounting"] = "CANONICAL"
        self.assertRule(d, "E_RND_ECONOMIC_AUTHORITY:")

    def test_presentation_economic_authority_rejected(self):
        d = self.load_catalog()
        r = next(x for x in d["repositories"] if x["system_kind"] == "PRESENTATION")
        r["authority"]["payment"] = "CANONICAL"
        self.assertRule(d, "E_PRESENTATION_ECONOMIC_AUTHORITY:")

    def test_ambiguous_exclusive_authority_rejected(self):
        d = self.load_catalog()
        other = next(x for x in d["repositories"] if x["name"] != "synergy_financial_os" and x["lifecycle_status"] == "CANONICAL")
        other["authority"]["accounting"] = "CANONICAL"
        self.assertRule(d, "E_AUTHORITY_AMBIGUOUS:")

    def test_successor_cycle_rejected(self):
        d = self.load_catalog()
        by = {x["name"]: x for x in d["repositories"]}
        by["midas_ai"]["canonical_successor"] = "midas_lite"
        by["midas_lite"]["canonical_successor"] = "midas_ai"
        self.assertRule(d, "E_SUCCESSOR_CYCLE:")

    def test_catalog_digest_is_deterministic(self):
        self.assertIsNotNone(self.mod, "scripts/federation_v5.py must exist")
        d = self.load_catalog()
        self.assertEqual(self.mod.catalog_digest(d), self.mod.catalog_digest(copy.deepcopy(d)))


if __name__ == "__main__":
    unittest.main()
