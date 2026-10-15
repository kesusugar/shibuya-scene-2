#!/usr/bin/env python3
"""Bounded MAGNET active-screen repair. Python 3 standard library only.

This is a binary-preserving patch, not a Blender re-export of the building.
The accepted baseline is an explicit portable input; all other geometry stays put.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

TARGET = '08_SIGNS_2025_box_screen'
BASELINE_SHA256 = 'fedc370e1242801366ddfb617e4a363a6097f092cf9b52f73eb55238e613d673'
sha = lambda b: hashlib.sha256(b).hexdigest()
compact = lambda v: json.dumps(v, separators=(',', ':'), ensure_ascii=False)
f32 = lambda v: struct.unpack('<f', struct.pack('<f', v))[0]


def read_glb(path):
    raw = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and length == len(raw)
    jl, jt = struct.unpack_from('<II', raw, 12)
    assert jt == 0x4e4f534a
    text = raw[20:20+jl].decode('utf-8')
    bl, bt = struct.unpack_from('<II', raw, 20+jl)
    assert bt == 0x004e4942 and 28+jl+bl == len(raw)
    return raw, text, json.loads(text), raw[28+jl:]


def values(doc, binary, index):
    a = doc['accessors'][index]
    v = doc['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and v.get('buffer', 0) == 0
    fmt, size = {5126: ('f', 4), 5125: ('I', 4), 5123: ('H', 2), 5121: ('B', 1)}[a['componentType']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    offset = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = v.get('byteStride', width*size)
    return [list(struct.unpack_from('<'+fmt*width, binary, offset+i*stride)) for i in range(a['count'])]


def repair(inputs, output):
    output.mkdir(parents=True, exist_ok=True)
    raw, text, doc, binary = read_glb(inputs/'magnet_signs_2025.before.glb')
    assert sha(raw) == BASELINE_SHA256, 'Wrong baseline: refuse to change another revision.'
    spec = json.loads((inputs/'screen_correction.json').read_text())
    nodes = [n for n in doc['nodes'] if n.get('name') == TARGET]
    assert len(nodes) == 1 and set(nodes[0]) == {'mesh', 'name'}
    primitives = doc['meshes'][nodes[0]['mesh']]['primitives']
    assert len(primitives) == 1
    primitive = primitives[0]
    ai = primitive['attributes']['POSITION']
    accessor = doc['accessors'][ai]
    view = doc['bufferViews'][accessor['bufferView']]
    assert accessor['count'] == 4 and accessor['componentType'] == 5126 and accessor['type'] == 'VEC3'
    assert view['byteLength'] == 48 and 'byteStride' not in view and 'byteOffset' not in accessor
    assert sum(p['attributes'].get('POSITION') == ai for m in doc['meshes'] for p in m['primitives']) == 1
    assert sum(a.get('bufferView') == accessor['bufferView'] for a in doc['accessors']) == 1
    old_vertices = values(doc, binary, ai)
    assert old_vertices == [[36.,14.,old_vertices[0][2]], [f32(43.6),14.,old_vertices[0][2]], [f32(43.6),23.,old_vertices[0][2]], [36.,23.,old_vertices[0][2]]]
    # glTF axes are (authoring X, authoring Z, -authoring Y). Preserve Y bytes.
    x0,x1 = spec['authoring']['x_m']; z0,z1 = spec['authoring']['z_m']
    corners = [(x0,z0), (x1,z0), (x1,z1), (x0,z1)]
    patched_bin = bytearray(binary)
    offset = view.get('byteOffset', 0)
    for i,(x,z) in enumerate(corners):
        struct.pack_into('<ff', patched_bin, offset+i*12, x,z)
    new_vertices = values(doc, patched_bin, ai)
    new_accessor = copy.deepcopy(accessor)
    new_accessor['min'] = [min(v[k] for v in new_vertices) for k in range(3)]
    new_accessor['max'] = [max(v[k] for v in new_vertices) for k in range(3)]
    old_json = compact(accessor)
    assert text.count(old_json) == 1, 'Expected one byte-exact accessor record.'
    patched_text = text.replace(old_json, compact(new_accessor), 1).rstrip(' ')
    json_bytes = patched_text.encode('utf-8')
    json_bytes += b' ' * (-len(json_bytes) % 4)
    patched = (struct.pack('<4sII', b'glTF', 2, 28+len(json_bytes)+len(patched_bin))
               + struct.pack('<II', len(json_bytes), 0x4e4f534a) + json_bytes
               + struct.pack('<II', len(patched_bin), 0x004e4942) + patched_bin)
    dest = output/'magnet_signs_2025.glb'
    dest.write_bytes(patched)

    # Correct only the intended source entry, preserving every other entry verbatim.
    source = (inputs/'signage_2025.before.json').read_text()
    old_line = next(line for line in source.splitlines() if '"id": "box_screen"' in line)
    new_line = old_line.replace('"z": [14.0, 23.0]', '"z": [16.46, 21.26]').replace('"x": [36.0, 43.6]', '"x": [35.48, 44.12]')
    new_line = new_line.replace('M014, M027 (screen in the grey box)', 'PAS 2021-03-08: active 8.64 x 4.80 m; HUIS 2025-10-24 release photo: normalized centre; inherited X/Y anchors; see screen_correction.json')
    assert old_line != new_line
    (output/'signage_2025.json').write_text(source.replace(old_line, new_line, 1))
    report = validate(inputs, output)
    (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def validate(inputs, output):
    before, text0, j0, b0 = read_glb(inputs/'magnet_signs_2025.before.glb')
    after, text1, j1, b1 = read_glb(output/'magnet_signs_2025.glb')
    node = next(n for n in j0['nodes'] if n.get('name') == TARGET)
    p = j0['meshes'][node['mesh']]['primitives'][0]; ai = p['attributes']['POSITION']
    jcheck = copy.deepcopy(j1); jcheck['accessors'][ai] = j0['accessors'][ai]
    assert jcheck == j0, 'Unexpected JSON / material / node / accessor mutation.'
    normalized_json = text1.rstrip().replace(compact(j1['accessors'][ai]), compact(j0['accessors'][ai]), 1)
    assert normalized_json == text0.rstrip(), 'Unexpected JSON byte change outside target accessor.'
    view = j0['bufferViews'][j0['accessors'][ai]['bufferView']]
    offset = view.get('byteOffset',0)
    allowed = {offset+i*12+k for i in range(4) for k in range(8)}
    changed = {i for i,(a,b) in enumerate(zip(b0,b1)) if a!=b}
    assert len(b0)==len(b1) and changed <= allowed and len(changed)>0
    verts = values(j1,b1,ai); old = values(j0,b0,ai)
    assert all(v[2] == old[i][2] for i,v in enumerate(verts)), 'Mounting plane moved.'
    assert max(abs(v[0]-t[0])+abs(v[1]-t[1]) for v,t in zip(verts,[(35.48,16.46),(44.12,16.46),(44.12,21.26),(35.48,21.26)])) < 0.00001
    assert values(j0,b0,p['indices']) == values(j1,b1,p['indices']) == [[0],[1],[2],[0],[2],[3]]
    assert values(j1,b1,p['attributes']['NORMAL']) == [[0,0,1]]*4
    assert values(j1,b1,p['attributes']['TEXCOORD_0']) == [[0,1],[1,1],[1,0],[0,0]]
    # Check every primitive, not just the target.
    tris=0; positions=0
    for mesh in j1['meshes']:
        for pr in mesh['primitives']:
            assert pr.get('mode',4) == 4 and 'material' in pr
            pp=values(j1,b1,pr['attributes']['POSITION']);positions+=len(pp)
            assert all(abs(c)<1e9 for v in pp for c in v)
            idx=values(j1,b1,pr['indices']) if 'indices' in pr else [[i] for i in range(len(pp))]
            assert len(idx)%3==0 and all(0<=v[0]<len(pp) for v in idx);tris+=len(idx)//3
    x=[v[0] for v in verts];z=[v[1] for v in verts]
    assert min(x)>35 and max(x)<44.6 and min(z)>9 and max(z)<32
    assert max(z)<26.6 and 8.7-(-verts[0][2])>0
    src0=json.loads((inputs/'signage_2025.before.json').read_text());src1=json.loads((output/'signage_2025.json').read_text())
    assert len(src0['signs'])==len(src1['signs'])
    for a,b in zip(src0['signs'],src1['signs']):
        if a['id']!='box_screen':assert a==b
        else:
            c=copy.deepcopy(b)
            for key in ['x','z','src']:c[key]=a[key]
            assert c==a
    manifest=json.loads((inputs/'baseline_manifest.json').read_text())
    for name,row in manifest.items():assert sha((inputs/name).read_bytes())==row['sha256'],name
    before_center=sum(v[0] for v in old)/4;after_center=sum(v[0] for v in verts)/4
    assert abs(before_center-after_center)<0.000002
    return {'status':'PASS','target':TARGET,'before_sha256':sha(before),'after_sha256':sha(after),
      'before_bytes':len(before),'after_bytes':len(after),'changed_binary_bytes':len(changed),
      'changed_position_components':8,'position_vertices':4,'target_triangles':2,'all_triangles':tris,
      'all_position_vertices':positions,'all_meshes':len(j1['meshes']),'all_materials':len(j1['materials']),
      'unchanged_binary_bytes_outside_target_position':True,'unchanged_json_bytes_except_accessor_bounds_and_padding':True,
      'all_nodes_materials_textures_images_indices_normals_uvs_unchanged':True,
      'all_other_signs_and_source_entries_unchanged':True,'main_building_and_eiraku_companion_hashes_verified':True,
      'authoring_vertices_m':[[v[0],-v[2],v[1]] for v in verts],
      'width_m':max(x)-min(x),'height_m':max(z)-min(z),'normal_authoring':[0,-1,0],
      'horizontal_center_change_m':after_center-before_center,
      'cassette_margins_m':{'left':min(x)-35,'right':44.6-max(x),'bottom':min(z)-9,'top':32-max(z)},
      'logo_clearance_m':26.6-max(z),'stand_off_m':8.7+verts[0][2],
      'authoring_datum':'inherited; no rebasing','runtime_offset_m':json.loads((inputs/'viewer.json').read_text())['groundElevationTP']-15,
      'no_fps_or_walking_tests':True}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent.parent/'inputs')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--validate-only',action='store_true')
    args=ap.parse_args()
    report=validate(args.inputs,args.output) if args.validate_only else repair(args.inputs,args.output)
    print(json.dumps(report,indent=2))
