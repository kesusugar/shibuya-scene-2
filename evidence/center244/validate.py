import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];A=R/'assets/buildings/center244';S=A/'source';OUT=A/'web';checks={}
assert bpy.app.version==(4,2,3)
D=json.loads((S/'data/plateau.json').read_text());checks['raw_source_hash']=hashlib.sha256((S/'data/plateau.json').read_bytes()).hexdigest();assert checks['raw_source_hash']=='3df9205722f35b952183fb20bae33fb67e6c30b0f273592f5ed5a753ca38dc3a'
bpy.ops.wm.read_factory_settings(use_empty=True)
for p in [OUT/'center244.glb',OUT/'signs-2025-01.glb']:bpy.ops.import_scene.gltf(filepath=str(p))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ps=[o.matrix_world@v.co for o in obs for v in o.data.vertices];bounds=[[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(3)];checks['actual_blender_xyz_bounds']=bounds
assert abs(bounds[2][1]-34.843)<.001
tris=sum(len(p.vertices)-2 for o in obs for p in o.data.polygons);bs=sum(p.stat().st_size for p in OUT.glob('*.glb'));checks.update(triangles=tris,primitives=len(obs),bytes=bs);assert tris<120000 and len(obs)<=40 and bs<3000000
assert 'layers' not in json.loads((OUT/'viewer.json').read_text())
checks['january_not_registered']=True
# Glass ray: exact front wall removed, so first hit must be recessed glazing/frame, never retained shell.
a=Vector((-66.643,72.26,0));b=Vector((-62.747,79.701,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));rays=[]
for u,z in [(2.1,14.9),(3.4,12),(4.9,8.6)]:
 p=a+t*u+Vector((0,0,z));hit=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),p+n*2,-n,distance=4)
 assert hit[0];distance=(hit[1]-p).dot(n);rays.append({'name':hit[4].name,'depth':distance});assert distance<-.10, rays
checks['window_recess_rays']=rays
# No front bracing over the ad face, including edges and middle.
a=Vector((-69.767,75.027,0));b=Vector((-65.264,80.842,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));rays=[]
for u in [0,2.7,6.8]:
 for z in [26.5,29.8,33.8]:
  p=a+t*u+Vector((0,0,z));hit=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),p+n*3,-n,distance=4);assert hit[0];rays.append(hit[4].name);assert 'ad_2025_01' in hit[4].name, rays
checks['billboard_front_rays']=rays
# Original complete rings remain in saved .blend as hidden reference, not runtime meshes.
bpy.ops.wm.open_mainfile(filepath=str(S/'blender/center244.blend'));o=bpy.data.objects['raw_plateau_exact_rings'];source=[tuple(p) for s in D['surfaces'] for p in s['ring'][:-1]];actual=[tuple(v.co) for v in o.data.vertices];assert len(source)==len(actual) and all(max(abs(a-b) for a,b in zip(p,q))<.00001 for p,q in zip(source,actual));assert o.hide_render and o.hide_viewport
checks['hidden_provenance_mesh_exact_within_float32']=True
checks['full_scene']='not run; complete scene assets unavailable';checks['fps']='not measured'
(Path(__file__).parent/'validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
