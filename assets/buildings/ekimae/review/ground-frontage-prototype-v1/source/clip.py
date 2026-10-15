"""Portable GLB triangle clipping. Keeps all original BIN bytes and nodes; appends changed accessors only."""
import struct,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
PIN='4ecb3412bc946a8aa88ac9ab0ac4d9f415b8d5bcadac819ead9d8d59885b89c8'
T=(.9991711854627296,-.04070555417880273);N=(.04070555417880273,.9991711854627296);B=(-46.78,-10.647)
def sha(b):return hashlib.sha256(b).hexdigest()
def key(ps):return '|'.join(','.join(f'{c:.4f}' for c in p) for p in sorted(tuple(round(c,4) for c in p) for p in ps))
def dkey(ps):return tuple(sorted(tuple(round(c,3) for c in p) for p in ps))
def parse(b):
 n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),bytearray(b[28+n:])
def acc(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];size=struct.calcsize('<'+fmt*k);o=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [tuple(struct.unpack_from('<'+fmt*k,b,o+j*v.get('byteStride',size))) for j in range(a['count'])]
def append(d,b,vals,typ,comp=5126):
 b.extend(b'\0'*((-len(b))%4));off=len(b);fmt='I' if comp==5125 else 'f'
 for v in vals:b.extend(struct.pack('<'+fmt*len(v),*v))
 vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(b)-off});a={'bufferView':vi,'componentType':comp,'count':len(vals),'type':typ}
 if typ=='VEC3':a.update(min=[min(v[j] for v in vals) for j in range(3)],max=[max(v[j] for v in vals) for j in range(3)])
 ai=len(d['accessors']);d['accessors'].append(a);return ai
def save(d,b,p):
 b.extend(b'\0'*((-len(b))%4));d['buffers'][0]['byteLength']=len(b);j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);p.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(b))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(b),b'BIN\0')+b)
def uvh(p):
 x,y,z=p;dx=x-B[0];dy=-z-B[1];return (-dx*T[0]-dy*T[1],dx*N[0]+dy*N[1],y)
# Cut only the façade depth prism below unchanged canopy. Upper polygons are split, not deleted.
planes=[(0,-1.7,1),(0,3.7,-1),(1,-1.1,1),(1,1.05,-1),(2,-.001,1),(2,2.98,-1)]
def split(poly,plane):
 axis,bound,sign=plane;inside=[];outside=[]
 for a,c in zip(poly,poly[1:]+poly[:1]):
  da=(uvh(a['POSITION'])[axis]-bound)*sign;dc=(uvh(c['POSITION'])[axis]-bound)*sign
  (inside if da>=-1e-9 else outside).append(a)
  if (da>1e-9 and dc< -1e-9) or (da< -1e-9 and dc>1e-9):
   t=da/(da-dc);p={k:tuple(x+(y-x)*t for x,y in zip(a[k],c[k])) for k in a};inside.append(p);outside.append(p)
 return inside,outside

def area(poly):
 if len(poly)<3:return 0
 p=poly[0]['POSITION'];v=0
 for a,b in zip(poly[1:-1],poly[2:]):
  aa=[a['POSITION'][j]-p[j] for j in range(3)];bb=[b['POSITION'][j]-p[j] for j in range(3)];v+=math.sqrt(sum((aa[(j+1)%3]*bb[(j+2)%3]-aa[(j+2)%3]*bb[(j+1)%3])**2 for j in range(3)))/2
 return v

def run():
 blob=(R/'input/ekimae.glb').read_bytes();assert sha(blob)==PIN;d,b=parse(blob);original_bin=bytes(b)
 sig=json.loads((R/'input/door-signatures.json').read_text());ds=-2.474595549250896
 door={m:{dkey([[p[0]-T[0]*ds,p[1],p[2]+T[1]*ds] for p in tri]) for tri in tris} for m,tris in sig['target'].items()}
 door_coordinates={m:{dkey([[p[0]-T[0]*ds,p[1],p[2]+T[1]*ds] for p in tri]):sorted(tuple([p[0]-T[0]*ds,p[1],p[2]+T[1]*ds]) for p in tri) for tri in tris} for m,tris in sig['target'].items()}
 max_door_error=0
 provenance=json.loads((R/'evidence/generator-provenance.json').read_text());audit=[];found={m:set() for m in door};upper_before=[];upper_after=[];untouched=0
 for mi,m in enumerate(d['meshes']):
  for pi,p in enumerate(m['primitives']):
   mat=d['materials'][p['material']]['name'];arrays={k:acc(d,b,v) for k,v in p['attributes'].items()};idx=[v[0] for v in acc(d,b,p['indices'])];newidx=[];newarrays={k:list(v) for k,v in arrays.items()};changed=False;added=False
   for ti in range(0,len(idx),3):
    ids=idx[ti:ti+3];poly=[{k:a[i] for k,a in arrays.items()} for i in ids];ps=[v['POSITION'] for v in poly];k=key(ps)
    if min(v[1] for v in ps)>=3.15-1e-6:upper_before.append((mat,k))
    dk=dkey(ps);isdoor=dk in door.get(mat,set())
    if isdoor:
     assert dk not in found[mat], 'Ambiguous repeated door signature'
     err=max(abs(a-b) for aa,bb in zip(sorted(ps),door_coordinates[mat][dk]) for a,b in zip(aa,bb));assert err<1e-5
     max_door_error=max(max_door_error,err);found[mat].add(dk);inside=poly;pieces=[]
    elif min(v[1] for v in ps)>=2.98-1e-6:inside=[];pieces=[poly]
    else:
     inside=poly;pieces=[]
     for plane in planes:
      inside,out=split(inside,plane)
      if area(out)>1e-10:pieces.append(out)
      if not inside:break
    if not isdoor and area(inside)<1e-9:
     newidx+=ids;untouched+=1
     if min(v[1] for v in ps)>=3.15-1e-6:upper_after.append((mat,k))
     continue
    changed=True
    source=provenance['triangles'].get(mat,{}).get(k,[])
    audit.append({'mesh':mi,'primitive':pi,'triangle':ti//3,'original_vertex_indices':ids,'material':mat,'source_face_ids':source,'source': [provenance['faces'][i] for i in source], 'reason':'exact_prior_door_signature' if isdoor else 'ground_prism_intersection','original_triangle':ps,'removed_area_m2':area(inside),'retained_pieces':[[v['POSITION'] for v in pp] for pp in pieces]})
    for pp in pieces:
     for j in range(1,len(pp)-1):
      tri=[pp[0],pp[j],pp[j+1]]
      if area(tri)<1e-10:continue
      for v in tri:
       newidx.append(len(newarrays['POSITION']))
       for name,a in newarrays.items():a.append(v[name])
      added=True
   if changed:
    if added:
     for name,a in newarrays.items():p['attributes'][name]=append(d,b,a,d['accessors'][p['attributes'][name]]['type'])
    p['indices']=append(d,b,[(i,) for i in newidx],'SCALAR',5125)
 assert all(found[m]==door[m] for m in door),[(m,len(found[m]),len(door[m])) for m in door]
 assert upper_before==upper_after
 assert bytes(b[:len(original_bin)])==original_bin
 save(d,b,R/'web/clipped-base.glb')
 report={'input_sha256':sha(blob),'cut_prism_u_d_h':[-1.7,3.7,-1.1,1.05,-.001,2.98],'unchanged_original_bin_prefix':True,'whole_upper_triangles_identical':len(upper_before),'untouched_triangles':untouched,'changed_triangles':audit,'old_door_max_signature_coordinate_error_m':max_door_error,'old_door_triangles_removed':sum(len(v) for v in found.values()),'unmatched_changed_non_door_triangles':sum(not a['source_face_ids'] and a['reason']!='exact_prior_door_signature' for a in audit)}
 (R/'evidence/changed-geometry-map.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='changed_triangles'})
if __name__=='__main__':run()
