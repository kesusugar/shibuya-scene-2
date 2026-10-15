import bpy,bmesh,json,sys,math
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(p/'hachiko_right_boulder.blend'));o=bpy.context.scene.objects['hachiko_right_boulder_study'];bm=bmesh.new();bm.from_mesh(o.data)
r={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'finite':all(math.isfinite(c) for v in bm.verts for c in v.co),'objects':len(bpy.context.scene.objects),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'transforms_identity':list(o.location)==[0,0,0] and list(o.scale)==[1,1,1]}
print(r);(p/'checks.json').write_text(json.dumps(r,indent=2))
