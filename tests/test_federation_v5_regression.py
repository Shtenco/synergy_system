from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CHECK=ROOT/"scripts"/"check_federation_v5.py"
CAT=ROOT/"config"/"repository_catalog_v5.json"

class FederationV5RegressionTests(unittest.TestCase):
    def run_check(self,*args):
        return subprocess.run(["python",str(CHECK),*args],cwd=ROOT,capture_output=True,text=True)

    def test_clean_repository_passes(self):
        self.assertTrue(CHECK.exists(),"check script must exist")
        cp=self.run_check()
        self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)

    def test_inventory_snapshot_mismatch_fails(self):
        catalog=json.loads(CAT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"inventory.json"
            names=[r["name"] for r in catalog["repositories"]][:-1]
            p.write_text(json.dumps({"repositories":names}),encoding="utf-8")
            cp=self.run_check("--inventory-json",str(p))
            self.assertNotEqual(cp.returncode,0)
            self.assertIn("E_INVENTORY_DRIFT",cp.stdout+cp.stderr)

    def test_generated_drift_fails(self):
        target=ROOT/"generated"/"authority_map_v5.json"
        original=target.read_bytes()
        try:
            target.write_bytes(original+b" ")
            cp=self.run_check()
            self.assertNotEqual(cp.returncode,0)
            self.assertIn("E_GENERATED_DRIFT",cp.stdout+cp.stderr)
        finally:
            target.write_bytes(original)

if __name__=="__main__":
    unittest.main()
