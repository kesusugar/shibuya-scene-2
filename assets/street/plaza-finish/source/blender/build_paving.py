"""Clip a thin material overlay to the existing sidewalk triangles without changing terrain."""
import bpy,json,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'ground/core/source/blender'))
from paving_boundary import partition
cfg,ground,out,stats=sys.argv[sys.argv.index('--')+1:][:4];D=json.load(open(cfg));cx,cy=D['centre_xy'];a=math.radians(D['yaw_deg']);co,si=math.cos(a),math.sin(a)
x0,y0,x1,y1=D['bounds_local_m'];poly=[(cx+x*co-y*si,cy+x*si+y*co) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground);verts=[];faces=[];area=0
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or not ob.name.startswith('ground_sidewalk'):continue
 ob.data.calc_loop_triangles()
 for t in ob.data.loop_triangles:
  points=[tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]
  if max(p[0] for p in points)<min(p[0] for p in poly) or min(p[0] for p in points)>max(p[0] for p in poly) or max(p[1] for p in points)<min(p[1] for p in poly) or min(p[1] for p in points)>max(p[1] for p in poly):continue
  for piece,inside in partition(points,poly):
   if not inside:continue
   ids=[]
   for x,y,z in piece:ids.append(len(verts));verts.append((x,y,z+D['render_offset_m']))
   faces.append(ids)
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
me=bpy.data.meshes.new('plaza_finish');me.from_pydata(verts,[],faces);me.uv_layers.new();me.update()
period=[v*n for v,n in zip(D['tile_size_m'],D['atlas_tiles'])]
for p in me.polygons:
 for i in p.loop_indices:
  v=me.vertices[me.loops[i].vertex_index].co;x,y=v.x-cx,v.y-cy;me.uv_layers.active.data[i].uv=((co*x+si*y)/period[0],(-si*x+co*y)/period[1])
ob=bpy.data.objects.new('plaza_finish',me);bpy.context.collection.objects.link(ob)
m=bpy.data.materials.new('ground_sidewalk_hachiko_stone');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Roughness'].default_value=.95;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(Path(cfg).parent/D['texture']));m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);me.materials.append(m)
bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_yup=True)
Path(stats).write_text(json.dumps({'layout':D,'polygon_xy':poly,'triangles':sum(len(f)-2 for f in faces),'vertices':len(verts),'height_offset_m':D['render_offset_m']},indent=1)+'\n')
