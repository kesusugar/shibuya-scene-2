"""Blender 4.2.3 validation of saved blend, GLB reimport and clean regeneration."""
import bpy, sys, json, time, math, hashlib, struct
from pathlib import Path
T=time.perf_counter();args=sys.argv[sys.argv.index('--')+1:];P=Path(args[0]).resolve();C=Path(args[1]).resolve();name='jr_hachiko_entrance_fascia_2025_v001'
assert bpy.app.version[:3]==(4,2,3)
report={'blender_version':bpy.app.version_string,'world_transform':None,'runtime_integrated':False,'source_photo_images_included':False}
bpy.ops.wm.open_mainfile(filepath=str(P/'model'/f'{name}.blend'))
root=bpy.data.objects['H_CV_002_JR_entry_fascia_early2025_UNPLACED'];assert tuple(root.location)==(0,0,0) and tuple(root.rotation_euler)==(0,0,0) and tuple(root.scale)==(1,1,1)
fonts=[f for f in bpy.data.fonts if f.filepath!='<builtin>'];assert fonts and all(f.packed_file is not None for f in fonts)
assert len([o for o in bpy.data.objects if o.type=='FONT'])==5
report['blend']={'opened':True,'root_identity':True,'packed_font_datablocks':len(fonts),'editable_text_objects':5,'external_images':len([i for i in bpy.data.images if i.source=='FILE']),'dated_parent_present':'DATED_2025_ENTRANCE_ONLY_SWITCH' in bpy.data.objects}
assert report['blend']['external_images']==0

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_glb(p):
 b=p.read_bytes();assert b[:4]==b'glTF';n,typ=struct.unpack_from('<II',b,12);assert typ==0x4E4F534A;return json.loads(b[20:20+n].decode())
original=P/'model'/f'{name}.glb';clean=C/'model'/f'{name}.glb';j=load_glb(original)
assert len(j.get('materials',[]))==4 and len(j.get('images',[]))==0 and len(j.get('textures',[]))==0
assert not any('uri' in b for b in j.get('buffers',[]))
roots=[n for n in j['nodes'] if n.get('name')=='H_CV_002_JR_entry_fascia_early2025_UNPLACED'];assert len(roots)==1
rr=roots[0];assert 'matrix' not in rr and 'translation' not in rr and 'rotation' not in rr and 'scale' not in rr
report['glb_structure']={'embedded_buffer_only':True,'materials':4,'images':0,'textures':0,'nodes':len(j['nodes']),'identity_root_json':True}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(original))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
assert max(abs(lo[0]+hi[0]),abs(lo[1]+hi[1]),abs(lo[2]))<1e-5,(lo,hi)
expected=[4.8,.202,1.12];dims=[hi[i]-lo[i] for i in range(3)];assert all(abs(dims[i]-expected[i])<1e-5 for i in range(3))
tri=0;deg=0
for o in meshes:
 o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  v=[o.data.vertices[k].co for k in t.vertices]
  if (v[1]-v[0]).cross(v[2]-v[0]).length*.5<1e-12:deg+=1
assert deg==0
report['reimport']={'pass':True,'mesh_objects':len(meshes),'triangles':tri,'degenerate_triangles':deg,'dimensions_m':dims,'bounds_min_blender_xyz_m':lo,'bounds_max_blender_xyz_m':hi,'bottom_center_origin':True}
report['clean_regeneration']={'original_glb_sha256':digest(original),'regenerated_glb_sha256':digest(clean),'byte_identical_glb':digest(original)==digest(clean)}
assert report['clean_regeneration']['byte_identical_glb']
report['validation_seconds']=round(time.perf_counter()-T,3);report['result']='PASS'
(P/'validation/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
