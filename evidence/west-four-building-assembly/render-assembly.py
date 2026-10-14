import bpy,json,math,sys,hashlib,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
root=Path(sys.argv[sys.argv.index('--')+1]).resolve(); out=Path(__file__).resolve().parent
assert bpy.app.version[:3]==(4,2,3),bpy.app.version_string
bpy.ops.wm.read_factory_settings(use_empty=True)
manifest=json.loads((out/'assembly-input-manifest.json').read_text()); inputs=manifest['inputs']
for item in inputs:
 data=(root/item['path']).read_bytes(); assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
bounds={}; groups={}
for bid in ['west-block','daiichi-kangin','ekimae','center244']:
 h=json.loads((root/'assets/buildings'/bid/'web/viewer.json').read_text()); objs=[]
 for item in inputs:
  if item['building']!=bid or not item['render']:continue
  old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(root/item['path']));new=set(bpy.data.objects)-old
  for ob in new:
   if ob.parent is None:ob.location.z+=h['groundElevationTP']-15
  objs+=list(new)
 bpy.context.view_layer.update(); groups[bid]=[o for o in objs if o.type=='MESH']
 pts=[o.matrix_world@v.co for o in groups[bid] for v in o.data.vertices]
 bounds[bid]={'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],'groundElevationTP':h['groundElevationTP'],'mesh_objects':len(groups[bid])}
pairs=[]
for a,b in itertools.combinations(bounds,2):
 A,B=bounds[a],bounds[b];g=[max(A['min'][i],B['min'][i])-min(A['max'][i],B['max'][i]) for i in range(3)]
 pair={'a':a,'b':b,'separating_gaps_m':dict(zip('XYZ',g)),'aabb_disjoint':any(x>0 for x in g)}
 if not pair['aabb_disjoint']:
  def bvh(ob):
   me=ob.data;me.calc_loop_triangles();return BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=1e-6)
  hits=[]
  for x,y in itertools.product(groups[a],groups[b]):
   n=len(bvh(x).overlap(bvh(y)))
   if n:hits.append({'mesh_a':x.name,'mesh_b':y.name,'triangle_surface_contacts':n})
  pair['geometry_surface_contacts']=hits;pair['caveat']='Triangle-surface check distinguishes AABB overlap; not a solid-containment or runtime collision certification.'
 pairs.append(pair)
(out/'assembly-bounds.json').write_text(json.dumps(bounds,indent=2));(out/'pairwise-aabb-check.json').write_text(json.dumps({'coordinates':'Blender X/Y plan, Z relative to TP15; no recentering','pairs':pairs},indent=2))
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:p.inputs['Emission Strength'].default_value=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.65,.65,.65);s.render.resolution_x=1800;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
bpy.ops.object.light_add(type='SUN',location=(-90,-100,130));l=bpy.context.object;l.rotation_euler=(Vector((-50,0,0))-l.location).to_track_quat('-Z','Y').to_euler();l.data.energy=2
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
projections={}
for name,pos,aim,scale in [('assembly-southeast',(140,-115,130),(-61,14,22),164),('assembly-plan',(-62,14,235),(-62,14,0),205)]:
 cam.data.ortho_scale=scale;cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 projections[name]={}
 for bid,b in bounds.items():
  target=Vector(((b['min'][0]+b['max'][0])/2,(b['min'][1]+b['max'][1])/2,b['max'][2]))
  p=world_to_camera_view(s,cam,target);projections[name][bid]=[p.x*1800,(1-p.y)*1400]
 s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
(out/'label-projections.json').write_text(json.dumps(projections,indent=2))
