#!/usr/bin/env python3
"""Read-only GLB container and mesh accessor verification (Python standard library)."""
from pathlib import Path
import argparse, hashlib, json, math, struct
parser=argparse.ArgumentParser();parser.add_argument('path',nargs='?',default=str(Path(__file__).with_name('policebox_visible_facade_2025_v001.glb')));parser.add_argument('--output');args=parser.parse_args()
p=Path(args.path);data=p.read_bytes();magic,version,length=struct.unpack_from('<4sII',data,0)
assert magic==b'glTF' and version==2 and length==len(data)
offset=12;chunks=[];g=None;binary=None
while offset<len(data):
    n,kind=struct.unpack_from('<II',data,offset);payload=data[offset+8:offset+8+n];chunks.append({'type':kind,'bytes':n});offset+=8+n
    if kind==0x4E4F534A:g=json.loads(payload)
    if kind==0x004E4942:binary=payload
assert g is not None and binary is not None
external_buffers=[x.get('uri') for x in g.get('buffers',[]) if 'uri' in x]
external_images=[x.get('uri') for x in g.get('images',[]) if 'uri' in x]
node_names=[n.get('name','') for n in g.get('nodes',[])]
review_names=[n for n in node_names if n.startswith('Review') or 'guide' in n.lower() or n in ['front','left_oblique','right_oblique','top_silhouette','confidence']]
assert not external_buffers and not external_images and not g.get('images') and not g.get('textures') and not g.get('cameras') and not review_names
components={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)};widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def accessor(i):
    ac=g['accessors'][i];bv=g['bufferViews'][ac['bufferView']];fmt,bs=components[ac['componentType']];w=widths[ac['type']];stride=bv.get('byteStride',bs*w);base=bv.get('byteOffset',0)+ac.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*w,binary,base+j*stride) for j in range(ac['count'])]
triangles=0;zero=0;nonfinite=0;primitives=0;zero_meshes={}
for m in g.get('meshes',[]):
    for pr in m['primitives']:
        primitives+=1;assert pr.get('mode',4)==4
        pos=accessor(pr['attributes']['POSITION']);nonfinite+=sum(not all(math.isfinite(v) for v in row) for row in pos)
        ids=[v[0] for v in accessor(pr['indices'])] if 'indices' in pr else list(range(len(pos)))
        assert len(ids)%3==0
        for j in range(0,len(ids),3):
            a,b,c=[pos[ids[j+k]] for k in range(3)]
            u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
            cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            if sum(q*q for q in cross)<1e-20:
                zero+=1;zero_meshes[m.get('name','?')]=zero_meshes.get(m.get('name','?'),0)+1
            triangles+=1
if zero or nonfinite:raise RuntimeError(str({'zero_area_triangles':zero,'zero_meshes':zero_meshes,'nonfinite':nonfinite}))
result={'glb':p.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'chunks':chunks,'nodes':len(g.get('nodes',[])),'meshes':len(g.get('meshes',[])),'primitives':primitives,'materials':len(g.get('materials',[])),'triangles':triangles,'zero_area_triangles':zero,'nonfinite_position_rows':nonfinite,'external_buffers':external_buffers,'external_images':external_images,'image_count':len(g.get('images',[])),'texture_count':len(g.get('textures',[])),'review_nodes':review_names,'camera_count':len(g.get('cameras',[])),'light_extension_present':'KHR_lights_punctual' in g.get('extensions',{}),'passed':True}
assert not result['light_extension_present']
text=json.dumps(result,indent=2)+'\n'
if args.output:Path(args.output).write_text(text)
print(text)
