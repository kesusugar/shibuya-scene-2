"""Exact independent reviewer probe, copied with only output and portable input paths changed."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P/'verification';L=json.loads((P/'geometry/layout.json').read_text());asset=P/'parco_terrace_candidate.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(asset));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();z=L['zones'][2];a=Vector(z['a']);b=Vector(z['b']);t=(b-a).normalized();n=Vector((-t.y,t.x));rows=[]
for i in range(1,75):
 u=z['length']*i/75
 for h in ([27,28.5,29.8,31,35,38.8] if u<11 else [30.5,31,35,38.8]):
  for degrees in [15,30,45,60,75]:
   # Inward ray rotated westward: potential leak behind scoped north end, not out the eastern opening.
   rad=math.radians(degrees);d=Vector((n.x*math.cos(rad)+n.y*math.sin(rad),-n.x*math.sin(rad)+n.y*math.cos(rad),0));p=a+t*u-n*.25;origin=Vector((p.x,p.y,h));hit,loc,norm,ix,obj,m=s.ray_cast(dg,origin,d,distance=100)
   rows.append({'u':u,'z':h,'angle_west_of_normal':degrees,'hit':hit,'object':obj.name if hit else None,'distance':(loc-origin).length if hit else None,'hit_xyz':list(loc) if hit else None})
report={'candidate_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'samples':len(rows),'no_hits':[r for r in rows if not r['hit']],'hits_farther25m':[r for r in rows if r['hit'] and r['distance']>25],'max_distance':max(r['distance'] for r in rows if r['hit'])}
(R/'independent-oblique-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

assert report['samples']==1920 and not report['no_hits'] and not report['hits_farther25m']
