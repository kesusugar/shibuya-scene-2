import json,sys,math
from pathlib import Path
from glb_helpers import load,acc,to_blender,sha
R=Path(__file__).resolve().parents[1];p=R/'output/combined/shibuya109.glb';j,b=load(p);g=json.loads((R/'inputs/ground-contact.json').read_text());tris=json.loads((R/'inputs/render-ground-context.json').read_text())['triangles']
def height(x,y):
 zz=[]
 for a,c,d in tris:
  den=(c[1]-d[1])*(a[0]-d[0])+(d[0]-c[0])*(a[1]-d[1])
  if abs(den)<1e-9:continue
  u=((c[1]-d[1])*(x-d[0])+(d[0]-c[0])*(y-d[1]))/den;v=((d[1]-a[1])*(x-d[0])+(a[0]-d[0])*(y-d[1]))/den
  if min(u,v,1-u-v)>=-1e-7:zz.append(u*a[2]+v*c[2]+(1-u-v)*d[2])
 assert zz,(x,y)
 return max(zz)
m=next(m for m in j['meshes'] if m['name']=='entrance_gold_open_frame');vs=[to_blender(v) for v in acc(j,b,m['primitives'][0]['attributes']['POSITION'])];checks=[]
for name in ['rear_left','rear_right','front_left','front_right']:
 point=g['points'][name];x,y=point['xy'];z=point['z'];foot=[v for v in vs if math.hypot(v[0]-x,v[1]-y)<.24 and abs(v[2]-z)<.07];assert len(foot)>=16
 error=max(abs(v[2]-height(v[0],v[1])) for v in foot);assert error<.00002,(name,error)
 checks.append({'name':name,'center_z':z,'sampled_base_vertices':len(foot),'maximum_error_m':error})
newmats=[m for m in j['materials'] if m['name'].startswith(('entrance_','phase2_'))];emissive=[m['name'] for m in newmats if any(m.get('emissiveFactor',[0,0,0]))];assert emissive==['entrance_white_identity'],emissive
out={'model_sha256':sha(p.read_bytes()),'ground_sha256':g['ground_glb_sha256'],'foot_base_checks':checks,'new_emissive_materials':emissive,'other_new_materials_nonemissive':True,'claim':'Exact contact with pinned model-ground triangles, not survey or fullscene.'};(R/'evidence/feet-materials-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
