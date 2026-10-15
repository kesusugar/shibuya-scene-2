"""Blender 4.2.3-only portable, hash-pinned roof connectivity layer.
Run: blender -b --python-exit-code 1 -P source/roof-repair-v1/repair.py
For independent reproduction: append -- --output-dir /path/to/new/output
The exported GLB is a byte patch, not a broad Blender round-trip. All other bytes
remain exact. The packed blend retains the prior scene and replaces only the
roof object's mesh with that exact current roof; source photography is packed
for inspection only, never assigned as a texture.
"""
import sys,json,struct,hashlib,argparse
from pathlib import Path
import bpy
assert bpy.app.version==(4,2,3), 'Use exact Blender 4.2.3'
HERE=Path(__file__).resolve().parent; ASSET=HERE.parent.parent
args=argparse.ArgumentParser();args.add_argument('--output-dir',type=Path)
a=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cfg=json.loads((HERE/'repair-config.json').read_text());ID=cfg['asset']
OUT=a.output_dir;glbpath=(OUT/f'{ID}.glb') if OUT else ASSET/'web'/f'{ID}.glb';blendpath=(OUT/'updated.blend') if OUT else HERE/'updated.blend';reportpath=(OUT/'repair-report.json') if OUT else HERE/'repair-report.json'
for p in [glbpath,blendpath,reportpath]:p.parent.mkdir(parents=True,exist_ok=True)
sha=lambda x:hashlib.sha256(x).hexdigest()
raw=(HERE/'prior.glb').read_bytes();assert sha(raw)==cfg['baseline_sha256']
assert sha((ASSET/'source/data/plateau.json').read_bytes())==cfg['source_sha256']
jl=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+jl]);bs=28+jl
assert j['meshes'][cfg['mesh_index']]['name']==cfg['mesh']
p=j['meshes'][cfg['mesh_index']]['primitives'][cfg['primitive']]
assert p['attributes']=={'POSITION':cfg['position_accessor'],'NORMAL':cfg['normal_accessor']}
def accessor(data,ai):
 ac=j['accessors'][ai];v=j['bufferViews'][ac['bufferView']];n={'VEC3':3,'SCALAR':1}[ac['type']];fmt={5126:'f',5123:'H'}[ac['componentType']];sz=struct.calcsize(fmt)*n;st=bs+v.get('byteOffset',0)+ac.get('byteOffset',0);stride=v.get('byteStride',sz)
 return [list(struct.unpack_from('<'+fmt*n,data,st+i*stride)) for i in range(ac['count'])],st,stride
oldidx,ist,istride=accessor(raw,cfg['index_accessor']);oldidx=[x[0] for x in oldidx];pos,_,_=accessor(raw,cfg['position_accessor']);oldnorm,nst,nstride=accessor(raw,cfg['normal_accessor'])
targets={t for f in cfg['targets'] for t in f['triangle_indices']};out=bytearray(raw)
for c in cfg['triangle_changes']:
 assert c['triangle'] in targets and oldidx[c['triangle']*3:c['triangle']*3+3]==c['old'];offset=ist+c['triangle']*3*istride;assert offset==c['glb_byte_offset'];struct.pack_into('<3H',out,offset,*c['new'])
sharing=[(mi,pi) for mi,m in enumerate(j['meshes']) for pi,q in enumerate(m['primitives']) if q['attributes'].get('NORMAL')==cfg['normal_accessor']]
assert sharing==[(cfg['mesh_index'],cfg['primitive'])]
for n in cfg['normal_changes']:
 vi=n['vertex'];owners=[t for t in range(len(oldidx)//3) if vi in oldidx[t*3:t*3+3]];assert owners==n['prior_triangle_owners'] and set(owners)<=targets;assert oldnorm[vi]==n['old'];offset=nst+vi*nstride;assert offset==n['glb_byte_offset'];struct.pack_into('<3f',out,offset,*n['new'])
changed=[i for i,(x,y) in enumerate(zip(raw,out)) if x!=y];allowed={i for r in cfg['allowed_byte_ranges'] for i in range(r['offset'],r['offset']+r['length'])};assert set(changed)<=allowed;assert len(out)==len(raw)
idx,_,_=accessor(out,cfg['index_accessor']);idx=[x[0] for x in idx];normals,_,_=accessor(out,cfg['normal_accessor'])
from collections import Counter
proof=[]
for f in cfg['targets']:
 ring=f['exact_exported_boundary_xyz'];sourcepos=[[v[0],-v[2],v[1]] for v in pos];edges=Counter();area=0.;vids=set()
 for t in f['replacement_triangles']:
  ti=t['triangle'];vv=idx[ti*3:ti*3+3];assert vv==t['indices'];vids.update(vv);bi=[ring.index(sourcepos[v]) for v in vv];assert bi==t['source_boundary_indices'];aa,bb,cc=[ring[v] for v in bi];cross=(bb[0]-aa[0])*(cc[1]-aa[1])-(bb[1]-aa[1])*(cc[0]-aa[0]);assert cross>1e-10;area+=cross/2
  assert all(normals[v]==[0.,1.,0.] for v in vv)
  for k in range(3):edges[tuple(sorted([bi[k],bi[(k+1)%3]]))]+=1
 boundary={tuple(sorted([i,(i+1)%len(ring)])) for i in range(len(ring))};assert {e for e,n in edges.items() if n==1}==boundary and all(n in [1,2] for n in edges.values());assert abs(area-f['exported_source_area_m2'])<1e-7
 ownership=[]
 for v in sorted(set(f['all_original_vertex_indices'])|vids):
  before=[t for t in range(len(oldidx)//3) if v in oldidx[t*3:t*3+3]];after=[t for t in range(len(idx)//3) if v in idx[t*3:t*3+3]];assert set(before+after)<=targets
  ownership.append({'vertex':v,'before_triangle_owners':before,'after_triangle_owners':after,'before_normal_gltf':oldnorm[v],'after_normal_gltf':normals[v]})
 proof.append({'source_index':f['source_index'],'triangle_indices':f['triangle_indices'],'triangles':len(f['triangle_indices']),'exported_source_area_m2':area,'boundary_edges_preserved':True,'all_target_used_normals_exact_up':True,'normal_ownership':ownership})
glbpath.write_bytes(out)
# Keep every prior scene object/material/world, changing ONLY target roof mesh.
bpy.ops.wm.open_mainfile(filepath=str(HERE/'prior.blend'));roof=bpy.data.objects.get(cfg['mesh']);assert roof is not None and roof.type=='MESH';assert all(abs(roof.matrix_world[i][k]-(1 if i==k else 0))<1e-9 for i in range(4) for k in range(4))
def object_signature(o):
 data={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world]}
 if o.type=='MESH':data.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[m.name if m else None for m in o.data.materials],material_indices=[p.material_index for p in o.data.polygons],smooth=[p.use_smooth for p in o.data.polygons])
 return sha(json.dumps(data,sort_keys=True).encode())
other={o.name:object_signature(o) for o in bpy.data.objects if o!=roof};oldimages={im.name:bool(im.packed_file) for im in bpy.data.images};mats=list(roof.data.materials);mesh=bpy.data.meshes.new(cfg['mesh']+'_roof_repair_v1');mesh.from_pydata([(v[0],-v[2],v[1]) for v in pos],[],[idx[i:i+3] for i in range(0,len(idx),3)]);mesh.update()
for m in mats:mesh.materials.append(m)
mesh.normals_split_custom_set([(normals[l.vertex_index][0],-normals[l.vertex_index][2],normals[l.vertex_index][1]) for l in mesh.loops]);roof.data=mesh
assert {o.name:object_signature(o) for o in bpy.data.objects if o!=roof}==other
# Retain already packed images and add all supplied reference crops, no texturing.
refs=[]
for path in sorted((ASSET/'source/refs').glob('*')):
 if path.suffix.lower() not in ['.jpg','.jpeg','.png']:continue
 im=bpy.data.images.load(str(path),check_existing=True);im.pack();im.use_fake_user=True;im.filepath='//../refs/'+path.name;refs.append({'name':im.name,'file':str(path.relative_to(ASSET)),'sha256':sha(path.read_bytes()),'packed':bool(im.packed_file)})
for im in bpy.data.images:
 if not im.packed_file:
  try:im.pack()
  except RuntimeError:raise AssertionError('Unpacked reference '+im.name)
 im.use_fake_user=True
assert all(bool(bpy.data.images[n].packed_file) for n in oldimages)
bpy.context.scene['roof_repair_stage']='roof-repair-v1';bpy.context.scene['current_glb_sha256']=sha(bytes(out));bpy.context.scene['roof_source_indices']=','.join(str(f['source_index']) for f in cfg['targets']);bpy.ops.wm.save_as_mainfile(filepath=str(blendpath),compress=True)
report={'asset':ID,'stage':cfg['stage'],'blender_version':bpy.app.version_string,'prior_glb_sha256':sha(raw),'current_glb_sha256':sha(bytes(out)),'glb_bytes':len(out),'changed_byte_count':len(changed),'changed_byte_offsets':changed,'allowed_byte_ranges':cfg['allowed_byte_ranges'],'position_bytes_unchanged':True,'all_other_bytes_unchanged':True,'json_chunk_unchanged':True,'materials_unchanged':True,'source_ring_file_unchanged':True,'target_proof':proof,'triangle_changes':cfg['triangle_changes'],'normal_changes':cfg['normal_changes'],'blend_other_object_signatures':other,'retained_prior_images':oldimages,'packed_references':refs,'scope_note':'Only enumerated source faces are repaired. No other roof, real notch, datum, shell coordinate or façade changes.'}
reportpath.write_text(json.dumps(report,indent=2)+'\n');print('ROOF_LAYER_SUCCESS',ID,sha(bytes(out)),len(changed))
