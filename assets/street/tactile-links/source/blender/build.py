import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,ground,out,stats=sys.argv[sys.argv.index('--')+1:];D=json.load(open(src));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground);bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith('ground_sidewalk'):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
bm=bmesh.new();samples=[];snaps=[]
for f in D['faces']:
 pts=[]
 for x,y,dz in f:
  hit=bvh.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))[0]
  if hit is None:
   q=bvh.find_nearest(Vector((x,y,.5)))[0]
   if q is None or (Vector((q.x,q.y))-Vector((x,y))).length>.002:raise ValueError('outside sidewalk: '+str((x,y)))
   snaps.append({'xy':[x,y],'snapped_xy':[q.x,q.y]});x,y=q.x,q.y;hit=q
  pts.append((x,y,hit.z+dz));samples.append({'xy':[x,y],'tp':hit.z+15,'offset':dz})
 try:bm.faces.new([bm.verts.new(p) for p in pts])
 except ValueError:pass
bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new('street_tactile_links');bm.to_mesh(me);bm.free();m=bpy.data.materials.new('street_tactile_yellow');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.72,.5,.025,1);p.inputs['Roughness'].default_value=.9;me.materials.append(m);o=bpy.data.objects.new('street_tactile_links',me);bpy.context.collection.objects.link(o);bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_yup=True)
Path(stats).write_text(json.dumps({'triangles':len(me.polygons),'tiles':D['tiles'],'routes':D['routes'],'contact_samples':samples[::max(1,len(samples)//160)],'edge_snaps':snaps,'overlap_with_prior_tiles_m2':D['overlap_with_prior_tiles_m2'],'status':D['status']},indent=1)+'\n');print(len(me.polygons),'triangles',len(snaps),'edge snaps')
