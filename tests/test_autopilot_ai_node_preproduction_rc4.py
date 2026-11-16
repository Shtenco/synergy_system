import copy,json,unittest
from pathlib import Path
from scripts.verify_autopilot_ai_node_preproduction_rc4 import verify
ROOT=Path(__file__).resolve().parents[1]
class RC4Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.v=json.loads((ROOT/'releases'/'synergy_autopilot_v5_ai_node_preproduction_rc4.json').read_text())
 def test_canonical(self): self.assertEqual(verify(copy.deepcopy(self.v)),'a7239ebf88b07f41b390120e3b3e23448e28548b3b9d981eb80a1fc014325803')
 def test_reject_old_registry(self):
  x=copy.deepcopy(self.v);x['federation_registry_v3_digest']='12bdca330d81b81ec0acb32cf974f12fb36c5e72e6a1fea8680dc5e8470b275d'
  with self.assertRaises(ValueError): verify(x)
 def test_reject_old_admission(self):
  x=copy.deepcopy(self.v);x['meta_os_admission_v3_digest']='4d3502dba28745b8a734c082ca0260cbbfd4ead11a1396537434844df9987ee3'
  with self.assertRaises(ValueError): verify(x)
 def test_reject_running(self):
  x=copy.deepcopy(self.v);x['current_running']=True
  with self.assertRaises(ValueError): verify(x)
 def test_reject_authority(self):
  x=copy.deepcopy(self.v);x['execution_authority']='ROOT'
  with self.assertRaises(ValueError): verify(x)
if __name__=='__main__':unittest.main()
