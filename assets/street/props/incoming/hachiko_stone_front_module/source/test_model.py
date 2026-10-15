"""Blender 4.2.3: geometry, cavity, origin and material checks, exits nonzero on failure."""
import bpy,bmesh,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'hachiko_stone_front_module.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==3
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
assert abs(lo[2])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[1]+hi[1])<1e-6
assert all(abs(x-y)<1e-5 for x,y in zip([hi[i]-lo[i] for i in range(3)],[2.344,.27,.59]))
assert all(math.isfinite(x) for p in points for x in p)
tris=0
bm=bmesh.new()
for o in meshes:
 m=o.data.copy();m.transform(o.matrix_world);bm.from_mesh(m);bpy.data.meshes.remove(m);o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:assert t.area>1e-10
 for mat in o.data.materials:
  principled=mat.node_tree.nodes.get('Principled BSDF');assert principled.inputs['Emission Strength'].default_value==0 or max(principled.inputs['Emission Color'].default_value[:3])==0
assert tris<2500
bvh=BVHTree.FromBMesh(bm);bm.free()
# At the opening, the frontmost geometry is behind the face; the adjacent stone remains at +.11.
center=bvh.ray_cast(Vector((0,1,.13)),Vector((0,-1,0)))[0];wall=bvh.ray_cast(Vector((.4,1,.30)),Vector((0,-1,0)))[0]
assert center is not None and center.y<.10,(center,wall)
assert wall is not None and abs(wall.y-.11)<1e-5
assert all(not o.name.startswith(('street_surround','street_hachiko','ground_')) for o in meshes)
res={'checks_passed':8,'triangles':tris,'mesh_count':len(meshes),'bounds_blender':[lo,hi],'aperture_first_hit_y':center.y,'stone_face_y':wall.y,'runtime_integration':'not performed','full_scene_fps':'not tested'}
(P/'evidence').mkdir(exist_ok=True)
(P/'evidence'/'geometry_checks.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
