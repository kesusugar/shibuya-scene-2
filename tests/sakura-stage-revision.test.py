"""Sakura cumulative north143 + upper east113 geometry regression. Stdlib only."""
from pathlib import Path
import sys,json,hashlib,struct,collections,subprocess,tempfile,math
A=Path(__file__).resolve().parents[1]/'assets/buildings/sakura-stage'
sys.path.insert(0,str(A/'source/blender'))
import build_north143 as N
import build as E

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def unpack(p):return N.load(p)
def tris(d,b,p):
 ids=[x[0] for x in N.accessor(d,b,p['indices'])];return [tuple(ids[i:i+3]) for i in range(0,len(ids),3)]
def area(v):
 a,b,c=v;u=[b[i]-a[i] for i in range(3)];w=[c[i]-a[i] for i in range(3)];return sum((u[(i+1)%3]*w[(i+2)%3]-u[(i+2)%3]*w[(i+1)%3])**2 for i in range(3))
base=A/'source/data/baseline.glb';north=A/'source/data/accepted-north143.glb';final=A/'web/sakura-stage.glb'
assert blob(base)=='b8974ae91875f9b3790b6f8f754098aeb6d43533'
assert blob(final)=='7fc031aa43a2c02b0b5d8969d43a5173bf1eef63'
d0,b0=unpack(base);dn,bn=unpack(north);df,bf=unpack(final)
assert d0['materials']==df['materials'][:len(d0['materials'])]
assert dn['materials']==df['materials']
for key in ['nodes','scenes','scene','extensionsUsed','extensionsRequired','textures','images','samplers']:
 assert dn.get(key)==df.get(key),key
for i,n in enumerate(d0['nodes']):assert n==df['nodes'][i]
removed={};zero0=zerof=0
for mi,m in enumerate(d0['meshes']):
 assert m['name']==df['meshes'][mi]['name'];removed[m['name']]=0
 for pi,p in enumerate(m['primitives']):
  pn=dn['meshes'][mi]['primitives'][pi];pf=df['meshes'][mi]['primitives'][pi]
  assert p['attributes']==pn['attributes']==pf['attributes'];assert p.get('material')==pf.get('material')
  for k,i in p['attributes'].items():assert N.accessor(d0,b0,i)==N.accessor(df,bf,pf['attributes'][k]),(m['name'],k)
  pos=N.accessor(d0,b0,p['attributes']['POSITION']);t0=tris(d0,b0,p);tn=tris(dn,bn,pn);tf=tris(df,bf,pf)
  keep=[t for t in t0 if m['name'] in ['sakura-stage_wall','sakura-stage_roof'] or not N.target_triangle(pos,t)]
  assert tn==keep,(m['name'],'north off-target sequence')
  removed[m['name']]=len(t0)-len(tn)
  if m['name']=='sakura-stage_frame':
   assert tf==[t for i,t in enumerate(tn) if i not in E.REMOVED_OFFSETS]
   key=json.loads((A/'source/data/east113-source-key.json').read_text()); counts=collections.Counter()
   for i in E.REMOVED_OFFSETS:
    pts=[N.source(pos[j]) for j in tn[i]];lo=min(x[2] for x in pts);hi=max(x[2] for x in pts)
    matches=[j for j,v in enumerate(key['current_X_brace_rows']) if j in (4,5,6,7) and abs(v['z'][0]-lo)<.04 and abs(v['z'][1]-hi)<.04];assert len(matches)==1;counts[matches[0]]+=1
   assert counts=={4:4,5:4,6:4,7:4}
  else:assert tf==tn,(m['name'],'east off-target sequence')
  zero0+=sum(area([pos[j] for j in t])<1e-16 for t in t0);zerof+=sum(area([pos[j] for j in t])<1e-16 for t in tf)
# All appended geometry is bounded to north143, retains normals/materials exactly from accepted output.
for mi in range(len(d0['meshes']),len(df['meshes'])):
 assert dn['meshes'][mi]==df['meshes'][mi]
 for p in df['meshes'][mi]['primitives']:
  pos=N.accessor(df,bf,p['attributes']['POSITION'])
  for v in pos:
   u,dep,z=N.coords(v);assert -.002<=u<=N.WIDTH+.002 and .06<dep<.55 and N.Z0-.002<=z<=N.Z1+.002,(u,dep,z)
  assert not any(area([pos[j] for j in t])<1e-16 for t in tris(df,bf,p))
assert zero0==zerof==8
assert sum(removed.values())==5122
count=sum(len(tris(df,bf,p)) for m in df['meshes'] for p in m['primitives']);prims=sum(len(m['primitives']) for m in df['meshes'])
assert count==31834 and prims==12 and final.stat().st_size==2783244
assert count<=120000 and prims<=40 and final.stat().st_size<=3000000
assert json.loads((A/'web/viewer.json').read_text())['groundElevationTP']==15
stats=json.loads((A/'source/data/stats.json').read_text());assert stats['roof_translation_m']==0
with tempfile.TemporaryDirectory() as tmp:
 for script,target in [('build_north143.py',north),('build.py',final)]:
  out=Path(tmp)/script.replace('.py','.glb');subprocess.run([sys.executable,str(A/'source/blender'/script),str(out)],check=True,stdout=subprocess.DEVNULL);assert sha(out)==sha(target)
print(json.dumps({'status':'PASS','baseline_blob':blob(base),'final_blob':blob(final),'north_removed':removed,'north_removed_total':sum(removed.values()),'east_removed_triangles':16,'final_triangles':count,'primitives':prims,'bytes':final.stat().st_size,'inherited_zero_area_triangles':8,'off_target_attributes_indices_materials_nodes':'exact','reproduction':'both stages byte-identical','datum':'unchanged'},indent=2))
