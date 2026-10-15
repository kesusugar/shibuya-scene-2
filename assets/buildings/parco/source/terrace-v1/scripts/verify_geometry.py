from pathlib import Path
import bpy,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];L=json.loads((ROOT/'geometry/layout.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'parco_terrace_candidate.glb'));dg=bpy.context.evaluated_depsgraph_get();s=bpy.context.scene
results=[]
for zone in L['zones']:
 a=Vector(zone['a']);b=Vector(zone['b']);tt=(b-a).normalized();out=Vector((tt.y,-tt.x));n=Vector((-tt.y,tt.x))
 samples={171:[(u,z) for u in [1.5,6,10,13,18.5] for z in [27.5,32.5]],108:[(u,z) for u in [3,7,11] for z in [27.5,35.5]],152:[(2,27.5),(6,27.5),(9,27.5),(13,32.5),(16,32.5),(18,32.5)]}[zone['face']]
 for u,z in samples:
  p=a+tt*u+out*2;org=Vector((p.x,p.y,z));d=Vector((n.x,n.y,0));hit,loc,norm,idx,obj,matrix=s.ray_cast(dg,org,d,distance=60)
  dep=(loc-org).length-2 if hit else None
  results.append({'face':zone['face'],'u_m':u,'z':z,'hit':hit,'first_hit_object':obj.name if hit else None,'first_hit_inward_depth_m':dep,'hit_xyz':list(loc) if hit else None,'outer_coarse_wall_obstructs':bool(hit and abs(dep)<.08 and obj.name=='parco_wall')})
dense=[]
for zone in L['zones']:
 a=Vector(zone['a']);b=Vector(zone['b']);tt=(b-a).normalized();out=Vector((tt.y,-tt.x));n=-out
 for j in range(1,40):
  u=zone['length']*j/40;floor=L['levels']['fiveF_z'] if zone['face']==152 and u>=11 else L['levels']['fourF_z'];top=34.7 if zone['face']==171 else 39.3
  for z in [floor+1.8,(floor+top)/2,top-.3]:
   p=a+tt*u+out*2;org=Vector((p.x,p.y,z));direction=Vector((n.x,n.y,0));hit,loc,norm,idx,obj,matrix=s.ray_cast(dg,org,direction,distance=60)
   depth=(loc-org).length-2 if hit else None
   if not hit or depth>25:dense.append({'face':zone['face'],'u':u,'z':z,'hit':obj.name if hit else None,'depth':depth})
# Physically closed volume definition: each new slab/core pane has side returns; global mesh is assembly, not fused watertight building.
report={'dense351ray_missing_or_over25m':dense,'raycast_tests':results,'no_original_front_wall_on_sampled_openings':not any(r['outer_coarse_wall_obstructs'] for r in results),'minimum_non_support_opening_depth_m':min(r['first_hit_inward_depth_m'] for r in results if r['hit'] and 'structure' not in r['first_hit_object']), 'scope':'Perpendicular ray through actual imported prototype GLB at two heights, excluding floor/rail heights; first hits demonstrate actual depth, not hidden front planes. Structure hits are real support/core objects, not a failure.','limitations':['Aperture structure is not a fully connected navigation/collision mesh.','Eastern3Fto4F escalator opening remains unmodeled because source roof47 must stay unchanged.','Importeddegenerate source index placeholders are intentional; no frontcoverfacesrender.','Absolute floorlevelTP25.278 for1F is bounded inference±.5m, not survey.']}
(ROOT/'verification/raycast-depth.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

assert not report['dense351ray_missing_or_over25m'] and report['no_original_front_wall_on_sampled_openings']
