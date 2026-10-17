from pathlib import Path
import struct,json,hashlib,math
R=Path(__file__).resolve().parents[1]
def read(path):
 b=Path(path).read_bytes();n,t=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);off=20+n;ln,typ=struct.unpack_from('<II',b,off);assert typ==0x004e4942;buf=b[off+8:off+8+ln];return d,buf
TYPES={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};FMT={5121:'B',5123:'H',5125:'I',5126:'f'}
def accessor(d,buf,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];fmt='<'+FMT[a['componentType']]*TYPES[a['type']];size=struct.calcsize(fmt);stride=v.get('byteStride',size);offset=v.get('byteOffset',0)+a.get('byteOffset',0);out=[struct.unpack_from(fmt,buf,offset+k*stride) for k in range(a['count'])];assert all(math.isfinite(x) for row in out for x in row);return out

def report(path):
 d,buf=read(path);meshes={};tris=0;prims=0
 for mesh_index,mesh in enumerate(d['meshes']):
  parts=[];mt=0
  for p in mesh['primitives']:
   a={k:accessor(d,buf,v) for k,v in p['attributes'].items()};indices=accessor(d,buf,p['indices']);nt=len(indices)//3;tris+=nt;mt+=nt;prims+=1
   parts.append({'attributes':a,'indices':indices,'material':d['materials'][p['material']]})
  node=next(n for n in d['nodes'] if n.get('mesh')==mesh_index);node_name=node['name']
  transform={k:node[k] for k in ('matrix','translation','rotation','scale') if k in node}
  parts.append({'node_transform':transform})
  meshes[node_name]={'node_transform':transform,'triangles':mt,'geometry_material_hash':hashlib.sha256(json.dumps(parts,sort_keys=True).encode()).hexdigest()}
 return {'file':Path(path).name,'bytes':Path(path).stat().st_size,'triangles':tris,'primitives':prims,'mesh_count':len(d['meshes']),'meshes':meshes,'materials':[{k:m[k] for k in ['name','alphaMode','doubleSided','alphaCutoff'] if k in m} for m in d['materials']],'texture_images':len(d.get('images',[]))}
a=report(R/'models/surround_before.glb');b=report(R/'models/hachiko_surround_v002.glb');c=report(R/'models/hachiko_low_shrubs_only_v002.glb')
unchanged={n:a['meshes'][n]['geometry_material_hash']==b['meshes'].get(n,{}).get('geometry_material_hash') for n in a['meshes'] if not any(x in n.lower() for x in ['needle','branch'])}
assert all(unchanged.values()),unchanged
before_shrub=sum(m['triangles'] for n,m in a['meshes'].items() if any(x in n.lower() for x in ['needle','branch']))
roots=json.loads((R/'models/shrub_roots.json').read_text());D=json.loads((R/'input/layout.json').read_text());S=json.loads((R/'input/original_stats.json').read_text());expected=[]
for seg in D['segments']:
 z=min(p['ground_z'] for v in S['items'] if v['id']==seg['id'] for p in v['contact_samples'])
 for i in range(3):expected.append([seg['x0']+.22+.25+(seg['x1']-seg['x0']-.44-.5)*i/2,-1.45,z+.49])
assert all(max(abs(a-b) for a,b in zip(e,r['local']))<1e-12 for e,r in zip(expected,roots))
result={'before':a,'after':b,'shrubs_only':c,'before_shrub_triangles':before_shrub,'new_shrub_triangles':c['triangles'],'unchanged_nonvegetation_meshes':unchanged,'root_positions_verified':len(roots),'root_tolerance_m':1e-12,'full_surround_triangle_reduction_pct':round((1-b['triangles']/a['triangles'])*100,2),'large_trees_and_generic_trees':'Not included, not read, not modified. No scene application code changed.','scope':'Component validation only, not full Three.js scene or FPS validation.'}
(R/'validation/asset_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['before','after','shrubs_only']},indent=2))
