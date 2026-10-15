"""Blender 4.2.3: deterministic, opaque narrow-leaf groundcover study."""
import bpy, math, random, sys, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else root/'output'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
rng=random.Random(9513); verts=[];faces=[]; mids=[]
# Three tightly grouped crowns, NOT a continuous lawn or claimed full footprint.
for crown,(cx,cy) in enumerate([(-.025,-.01),(.028,.005),(-.002,.026)]):
 for j in range(12):
  a=2*math.pi*j/12+rng.uniform(-.22,.22)
  reach=rng.uniform(.085,.18);peak=rng.uniform(.065,.125)
  if j%5==0:reach*=.65;peak*=1.18
  tip=rng.uniform(.018,.075);width=rng.uniform(.005,.009)
  start=len(verts);side=Vector((-math.sin(a),math.cos(a),0))
  twist=rng.uniform(-.35,.35)
  for k in range(8):
   t=k/7;ang=a+twist*t
   p=Vector((cx+reach*t*math.cos(ang),cy+reach*t*math.sin(ang),peak*math.sin(math.pi*t*.83)+tip*t))
   # Narrow keeled blades, widening above base, tapering to a pointed final vertex.
   w=width*(.55+.7*math.sin(math.pi*t))*(1-t)**.65
   if k==7:w=0
   verts.extend([tuple(p-side*w*.5),tuple(p+Vector((0,0,.0018*math.sin(math.pi*t)))),tuple(p+side*w*.5)])
  for k in range(7):
   a0=start+k*3;b=a0+3
   if k<6:
    faces.extend([(a0,b,b+1),(a0,b+1,a0+1),(a0+1,b+1,b+2),(a0+1,b+2,a0+2)]);mids.extend([j%2]*4)
   else:
    faces.extend([(a0,b+1,a0+1),(a0+1,b+1,a0+2)]);mids.extend([j%2]*2)
mesh=bpy.data.meshes.new('Curved_opaque_blades');mesh.from_pydata(verts,[],faces);mesh.update()
# Remove unused coincident tip vertices; all faces remain nondegenerate.
obj=bpy.data.objects.new('Hachiko_groundcover_tuft_ESTIMATED',mesh);s.collection.objects.link(obj)
for name,color in [('Leaf_deep_olive',(.018,.055,.014,1)),('Leaf_muted_green',(.035,.085,.025,1))]:
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=color;m.use_backface_culling=False
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.78
 mesh.materials.append(m)
for p,mi in zip(mesh.polygons,mids):p.material_index=mi;p.use_smooth=True
# Origin at exact mesh AABB bottom centre, metres, identity transforms.
lo=Vector(tuple(min(v.co[i] for v in mesh.vertices) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in mesh.vertices) for i in range(3)))
center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for v in mesh.vertices:v.co-=center
obj['source']='RuinDig/Yuki Uchida; Commons 2025-07-13_095; CC BY 4.0'
obj['scope']='Unplaced standalone study; species, scale and hidden crown structure inferred; no 2026 persistence claim'
bpy.context.view_layer.objects.active=obj;obj.select_set(True)
# Keep source geometry editable, no cameras/lights/ground in the model file.
s.render.filepath='//preview.png'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'groundcover.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'groundcover.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
stats={'blender':bpy.app.version_string,'triangles':len(faces),'materials':2,'meshes':1,'dimensions_m':list(hi-lo),'origin':'AABB bottom centre','seed':9513,'leaves':36,'alpha':'OPAQUE','placement':'none','dimensions':'estimated, not surveyed','photo_date':'2025-07-13','current_2026_persistence':'unconfirmed'}
(out/'stats.json').write_text(json.dumps(stats,indent=2)+'\n')
