"""Replace only six pinned legacy triangles with six traced lower112 white rectangles.
Python 3 + numpy, or Blender 4.2.3. No source-shell or generic-generator rebuild.
"""
import copy, hashlib, json, struct, sys
from pathlib import Path
import numpy as np

A = Path(__file__).resolve().parents[2]
R = A / 'source/data'
B = R / 'lower-panel-baseline'
BASELINE = '75753aec0940ab0cdb1bc82914918adf424bef0098aad95c020a1b983a06b82c'
raw = (B / 'stream.glb').read_bytes()
assert hashlib.sha256(raw).hexdigest() == BASELINE, 'Accepted upper-stage input changed'
jl = struct.unpack_from('<I', raw, 12)[0]
J = json.loads(raw[20:20+jl])
bin0 = raw[28+jl:]
data = bytearray(bin0)
trace = json.loads((R / 'lower-panel-trace.json').read_text())
assert trace['asset_sha256'] == BASELINE and trace['source_face'] == 112
origin = np.array(trace['q_origin'])
end = np.array(trace['q_end'])
width = np.linalg.norm(end-origin)
tangent = (end-origin)/width
normal = np.array([tangent[1], -tangent[0], 0.])
low, high = trace['source_z_limits']
pitch = trace['pitch_estimate_m']
# These are the exact accepted-GLB triangle IDs, not a nominal z-window clip.
# Old quads extend +/-0.005 m beyond their rows, including the stage boundary.
REMOVE = {594: [2605,2607,2604], 597: [2617,2619,2616],
          600: [2631,2633,2630], 1453: [2605,2606,2607],
          1456: [2617,2618,2619], 1459: [2631,2632,2633]}

def arr(ai):
    ac = J['accessors'][ai]; view = J['bufferViews'][ac['bufferView']]
    size = 3 if ac['type'] == 'VEC3' else 1
    return np.frombuffer(bin0, dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[ac['componentType']],
                         count=ac['count']*size,
                         offset=view.get('byteOffset',0)+ac.get('byteOffset',0)).reshape(-1,size).copy()

def add(values, typ, component, target):
    while len(data)%4: data.extend(b'\0')
    a = np.asarray(values, dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[component])
    if typ == 'SCALAR': a = a.reshape(-1)
    J['bufferViews'].append({'buffer':0,'byteOffset':len(data),'byteLength':a.nbytes,'target':target})
    data.extend(a.tobytes())
    ac = {'bufferView':len(J['bufferViews'])-1,'componentType':component,'count':len(a),'type':typ}
    if typ == 'VEC3': ac.update(min=a.min(0).astype(float).tolist(),max=a.max(0).astype(float).tolist())
    J['accessors'].append(ac)
    return len(J['accessors'])-1

before = sum(J['accessors'][p['indices']]['count']//3 for m in J['meshes'] for p in m['primitives'])
mesh = J['meshes'][2]
assert mesh['name'] == 'stream_spandrel' and len(mesh['primitives']) == 1
p = mesh['primitives'][0]
pos = arr(p['attributes']['POSITION']); normals = arr(p['attributes']['NORMAL'])
indices = arr(p['indices']).reshape(-1,3)
removed = []
for ti, expected in REMOVE.items():
    assert indices[ti].tolist() == expected, (ti, 'Pinned identity mismatch')
    xyz = pos[indices[ti]][:,[0,2,1]] * [1,-1,1]
    q = (xyz-origin)@tangent/width
    depth = (xyz-origin)@normal
    assert q.min() > .3999 and q.max() < .4501
    assert xyz[:,2].min() >= low-.0051 and xyz[:,2].max() <= high+.0051
    assert depth.min() > .1900 and depth.max() < .1903
    removed.append({'triangle_id':ti,'indices':expected,'positions_gltf':pos[indices[ti]].astype(float).tolist(),
                    'normals_gltf':normals[indices[ti]].astype(float).tolist()})
kept = [tri.tolist() for i,tri in enumerate(indices) if i not in REMOVE]
pp = pos.tolist(); nn = normals.tolist(); added = []
for rect in trace['photo_proposed_rectangles']:
    q0,q1 = rect['q']; r0,r1 = rect['rows']
    z0,z1 = high-r1*pitch, high-r0*pitch
    assert 0 <= q0 < q1 <= .55 and low-1e-10 <= z0 < z1 <= high+1e-10
    first = len(pp)
    for q,z in [(q0,z0),(q1,z0),(q1,z1),(q0,z1)]:
        xyz = origin+tangent*(q*width)+normal*.19+np.array([0,0,z])
        pp.append([xyz[0],xyz[2],-xyz[1]])
        nn.append([normal[0],normal[2],-normal[1]])
    kept.extend([[first,first+1,first+2],[first,first+2,first+3]])
    added.append({'q':[q0,q1],'rows':[r0,r1],'z':[z0,z1],'outward_depth_m':.19})
# Compact this one changed primitive, retaining all remaining vertex/normal values exactly.
used = sorted({v for tri in kept for v in tri})
vmap = {old:new for new,old in enumerate(used)}
p['attributes']['POSITION'] = add([pp[v] for v in used],'VEC3',5126,34962)
p['attributes']['NORMAL'] = add([nn[v] for v in used],'VEC3',5126,34962)
p['indices'] = add([[vmap[v] for v in tri] for tri in kept],'SCALAR',5123,34963)
# Copy untouched accessor bytes, preserve scene, materials, nodes and primitive properties.
used = sorted({ai for m in J['meshes'] for p in m['primitives'] for ai in [p['indices'],*p['attributes'].values()]})
amap = {old:new for new,old in enumerate(used)}
out = bytearray(); accessors = []; views = []
for ai in used:
    ac = copy.deepcopy(J['accessors'][ai]); bv = J['bufferViews'][ac['bufferView']]
    payload = data[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']]
    while len(out)%4: out.extend(b'\0')
    views.append({'buffer':0,'byteOffset':len(out),'byteLength':len(payload),'target':bv['target']})
    out.extend(payload); ac['bufferView']=len(views)-1; accessors.append(ac)
for m in J['meshes']:
    for p in m['primitives']:
        p['indices'] = amap[p['indices']]
        p['attributes'] = {k:amap[v] for k,v in p['attributes'].items()}
J['accessors'] = accessors; J['bufferViews'] = views; J['buffers'][0]['byteLength'] = len(out)
js = json.dumps(J,separators=(',',':'),ensure_ascii=False).encode(); js += b' '*((-len(js))%4)
out.extend(b'\0'*((-len(out))%4))
result = struct.pack('<III',0x46546c67,2,28+len(js)+len(out))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(out),0x004e4942)+out
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else (sys.argv[1:] if 'bpy' not in sys.modules else [])
target = Path(args[0]) if args else A/'web/stream.glb'
target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(result)
after = sum(J['accessors'][p['indices']]['count']//3 for m in J['meshes'] for p in m['primitives'])
report = {'stage':'lower112-six-white-rectangles','source_sha256':BASELINE,'output_sha256':hashlib.sha256(result).hexdigest(),
          'triangles_before':before,'triangles_after':after,'triangle_delta':after-before,
          'bytes_before':len(raw),'bytes_after':len(result),'byte_delta':len(result)-len(raw),
          'primitive_count':sum(len(m['primitives']) for m in J['meshes']), 'changed_mesh':'stream_spandrel',
          'removed_triangles':removed,'added_quads':added,'target_q_limits':[0,.55], 'target_z_limits':[low,high],
          'removal_scope':'Exact six pinned legacy triangles, including their +/-0.005 m row overhang. No spatial clipping of accepted upper geometry.',
          'spandrels_changed':False,'source_shell_roof_ground_untouched':True,'materials_nodes_unchanged':True,
          'inference':'December 1, 2025 static facade interpretation; not October proof. q/z mapping is approximate, not surveyed storeys.'}
(R/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['output_sha256','triangles_after','bytes_after','triangle_delta','byte_delta']}))
