"""Read-only verification after closing/reopening the packed editable blend."""
import bpy, hashlib, json
from pathlib import Path
A=Path(__file__).resolve().parents[2]; E=A/'evidence/cumulative-v2/lower'
bpy.ops.wm.open_mainfile(filepath=str(A/'source/blender/stream.blend'))
assert bpy.app.version==(4,2,3)
triangles=sum(len(p.vertices)-2 for o in bpy.data.objects if o.type=='MESH' for p in o.data.polygons)
assert triangles==32538 and not list(bpy.data.libraries)
assert len([o for o in bpy.data.objects if o.type=='MESH'])==8
expected=['reference-CC0.jpg','DEC01-lower112-left-unmarked.jpg','DEC01-lower112-six-rectangles.jpg']
images=[]
for name in expected:
    ref=bpy.data.images.get(name); assert ref is not None and ref.packed_file and ref.use_fake_user
    assert ref.filepath.startswith('//'),ref.filepath
    content=bytes(ref.packed_file.data); local=(A/'source/refs'/name).read_bytes(); assert content==local
    images.append({'name':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'packed':True,'fake_user':True,'relative_path':ref.filepath})
assert len([i for i in bpy.data.images if i.source=='FILE'])==len(expected)
embedded=['build.py','test.py','test-panel-rhythm.py','render.py','verify_blend.py','lower-panel-trace.json','build-report.json','LOWER-PANEL-SOURCE.md']
for name in embedded:
    text=bpy.data.texts.get(name); assert text
    path=A/'source/blender'/name if name.endswith('.py') else A/'source/data'/name if name.endswith('.json') else A/'source/refs'/name
    assert text.as_string()==path.read_text(),name
# Verify every scene mesh vertex/normal/triangle against the current GLB through a second import.
# Importer object transforms are preserved; no reconstructed shell or transformed geometry accepted.
def signatures():
    out={}
    for o in bpy.data.objects:
        if o.type!='MESH':continue
        out[o.name]=(tuple(tuple(float(x) for x in v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(float(x) for x in n.vector) for n in o.data.corner_normals),tuple(tuple(float(x) for x in row) for row in o.matrix_world))
    return out
saved=signatures(); bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=str(A/'web/stream.glb')); imported=signatures(); assert saved==imported
result={'pass':True,'blender':'4.2.3','triangles':triangles,'mesh_objects':8,'external_libraries':0,'all_file_images_packed':True,'images':images,'embedded_source_matches_files':True,'reopened_mesh_geometry_normals_and_transforms_match_runtime':True,'blend_byte_identity_claimed':False}
E.mkdir(parents=True,exist_ok=True); (E/'blend-verification.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
