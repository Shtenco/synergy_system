import copy,json,unittest
from pathlib import Path
from scripts.verify_autopilot_ai_node_preproduction_rc3 import verify
ROOT=Path(__file__).resolve().parents[1]
class RC3Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.v=json.loads((ROOT/'releases'/'synergy_autopilot_v5_ai_node_preproduction_rc3.json').read_text())
 def test_canonical(self): self.assertEqual(verify(copy.deepcopy(self.v)),'be8ca90e514e72ddccdc67a38cdd9b8321c2b55eb17ba6f04a9c65dbd4a16129')
 def test_reject_old_locator(self):
  x=copy.deepcopy(self.v); x['synergynet_location_evidence_v3_digest']=x['synergynet_previous_location_evidence_digest']
  with self.assertRaises(ValueError): verify(x)
 def test_reject_running(self):
  x=copy.deepcopy(self.v); x['current_running']=True
  with self.assertRaises(ValueError): verify(x)
 def test_reject_authority(self):
  x=copy.deepcopy(self.v); x['execution_authority']='ROOT'
  with self.assertRaises(ValueError): verify(x)
if __name__=='__main__': unittest.main()
