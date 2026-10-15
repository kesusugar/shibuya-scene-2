import unittest,json,struct,math
from repair import ROOT,parse,access,sha,PIN,key
class RepairTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.b=(ROOT/'input/ekimae.glb').read_bytes();c.a=(ROOT/'web/ekimae.glb').read_bytes();c.d,c.base=parse(c.b);c.e,c.ebase=parse(c.a);c.audit=json.loads((ROOT/'evidence/audit.json').read_text());c.sig=json.loads((ROOT/'source/signatures.json').read_text())
 def test_pinned_source(self):self.assertEqual(sha(self.b),PIN)
 def test_triangle_scope(self):
  self.assertEqual(sum(v['vertices'] for v in self.audit['selection']),168);self.assertEqual(sum(v['triangles'] for v in self.audit['selection']),84)
 def test_pier_clearance(self):self.assertAlmostEqual(self.audit['actual_pier_clearance_m'],.05,places=5)
 def test_canopy_containment(self):self.assertAlmostEqual(self.audit['actual_canopy_end_margin_m'],.7,places=5)
 def test_first_door_preserved(self):
  n=0
  for m in self.d['meshes']:
   for p in m['primitives']:
    mat=self.d['materials'][p['material']]['name']
    if mat not in self.sig['first_door']:continue
    sigs={key(t) for t in self.sig['first_door'][mat]};v,o=access(self.d,self.b,self.base,p['attributes']['POSITION']);av,ao=access(self.e,self.a,self.ebase,p['attributes']['POSITION']);ind,_=access(self.d,self.b,self.base,p['indices']);ind=[x[0] for x in ind]
    for i in range(0,len(ind),3):
     ids=ind[i:i+3]
     if key([v[j] for j in ids]) in sigs:
      n+=1
      for j in ids:self.assertEqual(v[j],av[j])
  self.assertEqual(n,84)
 def test_all_unrelated_bin_bytes(self):
  ranges=self.audit['allowed_position_ranges'];allowed={i-self.base for a,z in ranges for i in range(a,z)};old=self.b[self.base:];new=self.a[self.ebase:];self.assertEqual(len(old),len(new));self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(old,new))))
if __name__=='__main__':unittest.main()
