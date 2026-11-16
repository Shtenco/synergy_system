import copy,unittest
from synergy_system.autopilot_ai_node_registry_v3 import load_default,verify
class RegistryV3Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.v=load_default()
 def test_canonical(self): self.assertEqual(verify(copy.deepcopy(self.v)),'af24fe8c4b3ddfd8832f7e5ac6d92b2d4d69761cb9ab869407cd4d085e475526')
 def test_reject_old_transport(self):
  x=copy.deepcopy(self.v);x['synergynet_transport_binding_v2_digest']='3c8198e10863c52c0492ca422c404a1e05e6fd2f48f4c393587d9d87eee3855f'
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
