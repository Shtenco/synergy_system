from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"scripts"/"generate_federation_v5.py"
EXPECTED={
 "repository_registry_v5.json",
 "authority_map_v5.json",
 "capability_registry_v2.json",
 "federation_trust_source_v5.json",
 "exchange_object_registry_v1.json",
 "federation_graph_v5.json",
 "FEDERATION_STATUS_MATRIX.md",
}

class FederationV5GenerationTests(unittest.TestCase):
    def generate(self,path:Path):
        cp=subprocess.run(["python",str(GEN),"--output-dir",str(path)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)

    def test_generator_is_byte_deterministic(self):
        self.assertTrue(GEN.exists(),"generator must exist")
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            pa,pb=Path(a),Path(b)
            self.generate(pa); self.generate(pb)
            self.assertEqual({p.name for p in pa.iterdir()},EXPECTED)
            self.assertEqual({p.name for p in pb.iterdir()},EXPECTED)
            for name in EXPECTED:
                self.assertEqual((pa/name).read_bytes(),(pb/name).read_bytes(),name)

    def test_every_generated_json_binds_same_catalog_digest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); self.generate(p)
            digests=set()
            for path in p.glob("*.json"):
                digests.add(json.loads(path.read_text(encoding="utf-8"))["catalog_digest"])
            self.assertEqual(len(digests),1)
            self.assertNotIn(None,digests)

    def test_repository_count_is_derived(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); self.generate(p)
            reg=json.loads((p/"repository_registry_v5.json").read_text(encoding="utf-8"))
            trust=json.loads((p/"federation_trust_source_v5.json").read_text(encoding="utf-8"))
            self.assertEqual(reg["repository_count"],len(reg["repositories"]))
            self.assertEqual(trust["policy"]["repository_count"],len(trust["repositories"]))

if __name__=="__main__":
    unittest.main()
