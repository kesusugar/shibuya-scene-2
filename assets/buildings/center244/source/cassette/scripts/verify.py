"""Positive geometry and immutable-prefix acceptance checks. No Blender dependencies."""
import sys,json,struct,math,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from add_cassette import read_glb,ROOT,specs

def values(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC3':3}[a['type']];fmt={5123:'H',5126:'f',5125:'I'}[a['componentType']];size=struct.calcsize(fmt)*width;stride=v.get('byteStride',size);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 assert offset+(a['count']-1)*stride+size<=len(b)
 return [struct.unpack_from('<'+fmt*width,b,offset+i*stride) for i in range(a['count'])]
def main():
 old,ob=read_glb(ROOT/'inputs/center244.glb');new,nb=read_glb(ROOT/'output/center244.glb');q=json.loads((ROOT/'inputs/PROPOSAL.json').read_text());pins=json.loads((ROOT/'inputs/PINS.json').read_text())
 for name,h in pins.items():assert hashlib.sha256((ROOT/'inputs'/name).read_bytes()).hexdigest()==h
 assert nb[:len(ob)]==ob
 for k in ['nodes','meshes','materials','accessors','bufferViews']:assert new[k][:len(old[k])]==old[k],k
 assert new['asset']==old['asset'];assert new.get('scene')==old.get('scene')
 expected=json.loads(json.dumps(old['scenes']));expected[new.get('scene',0)]['nodes'].append(len(old['nodes']));assert new['scenes']==expected
 assert len(new['nodes'])==len(old['nodes'])+1 and len(new['meshes'])==len(old['meshes'])+1 and len(new['materials'])==len(old['materials'])+2
 assert new['nodes'][-1]=={'mesh':len(old['meshes']),'name':'c244_chamfer_cassette'}
 assert json.loads((ROOT/'inputs/viewer.json').read_text())['groundElevationTP']==15
 prim=new['meshes'][-1]['primitives'];assert len(prim)==2
 local=[];triangles=0;min_area=1e9;volumes=[]
 for group,p in enumerate(prim):
  assert p['mode']==4 and set(p['attributes'])=={'POSITION','NORMAL'};assert p['material']==len(old['materials'])+group
  pos=values(new,nb,p['attributes']['POSITION']);norm=values(new,nb,p['attributes']['NORMAL']);ind=[i[0] for i in values(new,nb,p['indices'])];assert len(ind)%3==0;triangles+=len(ind)//3
  assert len(pos)==len(norm);assert all(math.isfinite(v) for xyz in pos+norm for v in xyz)
  for x,z,ny in pos:
   dx=x-q['origin_a'][0];dy=-ny-q['origin_a'][1];local.append((dx*q['tangent'][0]+dy*q['tangent'][1],dx*q['outward'][0]+dy*q['outward'][1],z))
  for start in range(0,len(pos),24):
   volume=0
   for k in range(start//24*36,start//24*36+36,3):
    ids=ind[k:k+3];assert all(0<=i<len(pos) for i in ids);a,b,c=[pos[i] for i in ids];ab=[b[i]-a[i] for i in range(3)];ac=[c[i]-a[i] for i in range(3)];cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];area=sum(v*v for v in cross)**.5/2;assert area>1e-8;min_area=min(min_area,area);assert sum(cross[i]*norm[ids[0]][i] for i in range(3))>0
    volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
   assert volume>0;volumes.append(volume)
 assert triangles==48 and triangles<=120
 bounds=[[min(v[i] for v in local),max(v[i] for v in local)] for i in range(3)]
 for b,e in zip(bounds,[q['local_bounds']['u'],q['local_bounds']['outward_d'],q['local_bounds']['z']]):assert all(abs(x-y)<1e-5 for x,y in zip(b,e)),(b,e)
 for mat in new['materials'][-2:]:
  assert 'emissiveFactor' not in mat and 'extensions' not in mat and not mat['doubleSided'];assert not any('Texture' in key for key in mat['pbrMetallicRoughness'])
 assert bounds[2][0]>4.30 and bounds[2][1]<4.75
 assert bounds[0][0]>0 and bounds[0][1]<q['face_width_m']
 assert bounds[1][0]>.04
 report={'pass':True,'added_triangles':triangles,'added_material_primitives':len(prim),'original_binary_prefix_bytes':len(ob),'old_arrays_exact_prefix':True,'original_scene_nodes_preserved':True,'original_inputs_sha256':pins,'actual_local_bounds_u_d_z':bounds,'minimum_triangle_area_m2':min_area,'positive_closed_component_volumes_m3':volumes,'opening_vertical_clearance_m':bounds[2][0]-4.30,'upper_panel_vertical_clearance_m':4.75-bounds[2][1],'rear_trim_gap_m':bounds[1][0]-.04,'physical_wall_contact':False,'gap_disclosure':'Estimated envelope leaves 15 mm behind casing to existing trim; no invented brackets, no literal wall-contact claim.','candidate_sha256':hashlib.sha256((ROOT/'output/center244.glb').read_bytes()).hexdigest()}
 (ROOT/'evidence/verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
