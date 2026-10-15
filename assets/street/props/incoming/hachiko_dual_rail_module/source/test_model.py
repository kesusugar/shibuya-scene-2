import bpy,sys,json,math
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'hachiko_dual_rail_module.glb'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
assert all(math.isfinite(c) for v in vs for c in v)
assert len(obs)==1
assert abs(lo[2])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[1]+hi[1])<1e-6
assert abs(hi[0]-lo[0]-2.262)<1e-5 and abs(hi[1]-lo[1]-.290)<1e-5 and abs(hi[2]-.845)<1e-5
assert len(obs[0].data.materials)==1
assert sum(len(f.vertices)-2 for o in obs for f in o.data.polygons)==216
assert not bpy.data.images
for o in obs:
 assert o.location.length<1e-6
 for p in o.data.polygons:assert p.area>1e-10
assert len([v for v in vs if abs(v.z)<1e-6])>=8
result={'passed':True,'blender':bpy.app.version_string,'bounds':[lo,hi],'triangles':216,'materials':1,'no_textures':True,'scope':'standalone GLB; no runtime/full scene test'}
(R/'evidence'/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
