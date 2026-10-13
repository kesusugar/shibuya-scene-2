"""Blender 4.2.3 CLI: solid maintenance lid draped onto the existing road."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
layout,ground,output,stats=sys.argv[sys.argv.index('--')+1:][:4]
D=json.load(open(layout));cx,cy=D['cover']['centre_xy'];radius=D['cover']['diameter_m']/2
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_intersection')):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
verts=[];faces=[];slots=[];samples=[]
def face(points,slot,offset):
 indices=[]
 for x,y in points:
  hit=bvh.ray_cast(Vector((cx+x,cy+y,50)),Vector((0,0,-1)))
  if hit[0] is None:raise ValueError('cover outside existing road')
  indices.append(len(verts));verts.append((cx+x,cy+y,hit[0].z+offset));samples.append([cx+x,cy+y,hit[0].z,offset])
 faces.append(indices);slots.append(slot)
def ring(inner,outer,slot,offset):
 for i in range(96):
  a=i*math.tau/96;b=(i+1)*math.tau/96
  oa=outer if slot!=2 else outer+.009*math.sin(3*a)+.006*math.sin(7*a)
  ob=outer if slot!=2 else outer+.009*math.sin(3*b)+.006*math.sin(7*b)
  face([(inner*math.cos(a),inner*math.sin(a)),(oa*math.cos(a),oa*math.sin(a)),(ob*math.cos(b),ob*math.sin(b)),(inner*math.cos(b),inner*math.sin(b))],slot,offset)
base=D['base_offset_m']
# The light repair surround and procedural diamond relief are approximations, not photo textures.
ring(radius+.015,radius+.085,2,base)
ring(radius-.012,radius+.015,1,base+.0005)
for i in range(96):
 a=i*math.tau/96;b=(i+1)*math.tau/96
 face([(0,0),((radius-.012)*math.cos(a),(radius-.012)*math.sin(a)),((radius-.012)*math.cos(b),(radius-.012)*math.sin(b))],0,base)
for i in range(-11,12):
 for j in range(-11,12):
  x=i*.019;y=j*.019;r=.006
  points=[(x-r,y),(x,y-r),(x+r,y),(x,y+r)]
  if all(math.hypot(px,py)<radius-.018 for px,py in points):face(points,1,base+D['relief_m'])
me=bpy.data.meshes.new('street_drainage');me.from_pydata(verts,[],faces);me.update()
ob=bpy.data.objects.new('street_drainage',me);bpy.context.collection.objects.link(ob)
for name,color,metal,rough in [('lid',(.025,.028,.030),.55,.88),('rim_relief',(.055,.06,.063),.65,.8),('repair',(.21,.20,.18),0,.98)]:
 mat=bpy.data.materials.new('street_cover_'+name);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;me.materials.append(mat)
for p,slot in zip(me.polygons,slots):p.material_index=slot
bpy.ops.export_scene.gltf(filepath=output,export_format='GLB',export_yup=True,export_normals=True,export_materials='EXPORT')
Path(stats).write_text(json.dumps({'cover':D['cover'],'triangles':sum(len(f)-2 for f in faces),'vertices':len(verts),'contact_check':{'count':len(samples),'missing':0,'min_offset_m':base,'max_offset_m':base+D['relief_m']},'contact_samples':samples[::max(1,len(samples)//120)]},indent=1)+'\n')
