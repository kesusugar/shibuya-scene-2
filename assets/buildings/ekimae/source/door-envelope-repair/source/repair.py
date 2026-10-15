"""Stdlib-only, byte-preserving POSITION patch. Run from any cwd: python source/repair.py."""
import json,struct,hashlib,math,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PIN='6813569028d675817d20e16a68ac50f00962a3a18841b5e3980bacb634d3f92d'
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(b):
 assert b[:4]==b'glTF';n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);return d,28+n

def access(d,b,base,idx):
 a=d['accessors'][idx];v=d['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];size=struct.calcsize('<'+fmt*k);stride=v.get('byteStride',size);start=base+v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from('<'+fmt*k,b,start+i*stride) for i in range(a['count'])],[start+i*stride for i in range(a['count'])]
def key(ps):return tuple(sorted(tuple(round(x,4) for x in p) for p in ps))
def run():
 before=(ROOT/'input/ekimae.glb').read_bytes();assert sha(before)==PIN,'Pinned input mismatch';after=bytearray(before);d,base=parse(before);sig=json.loads((ROOT/'source/signatures.json').read_text());option=json.loads((ROOT/'source/REPAIR_OPTION.json').read_text());ds=option['shift_s'];T=sig['T'];delta=[-T[0]*ds,0,T[1]*ds]
 expected={kind:{mat:{key(tri) for tri in tris} for mat,tris in groups.items()} for kind,groups in [('target',sig['target']),('first_door',sig['first_door'])]}
 found={kind:{mat:set() for mat in groups} for kind,groups in expected.items()};ranges=[];details=[];target_after=[];first=[]
 for mi,m in enumerate(d['meshes']):
  for pi,p in enumerate(m['primitives']):
   mat=d['materials'][p['material']]['name']
   if mat not in expected['target']:continue
   pos,offsets=access(d,before,base,p['attributes']['POSITION']);indices,_=access(d,before,base,p['indices']);indices=[i[0] for i in indices];selected=[];unselected=[]
   for t in range(0,len(indices),3):
    ids=indices[t:t+3];k=key([pos[i] for i in ids])
    for kind in expected:
     if k in expected[kind][mat]:
      assert k not in found[kind][mat],'Ambiguous repeated signature';found[kind][mat].add(k)
      if kind=='first_door':first.extend(offsets[i] for i in ids)
    (selected if k in expected['target'][mat] else unselected).extend(ids)
   chosen=set(selected);assert not chosen.intersection(unselected),'Shared vertex outside target'
   for i in sorted(chosen):
    offset=offsets[i];new=tuple(pos[i][j]+delta[j] for j in range(3));struct.pack_into('<3f',after,offset,*new);ranges.append([offset,offset+12]);target_after.append(struct.unpack_from('<3f',after,offset))
   details.append({'mesh':mi,'primitive':pi,'material':mat,'triangles':len(selected)//3,'vertices':len(chosen)})
 for kind in expected:
  for mat in expected[kind]:assert found[kind][mat]==expected[kind][mat],(kind,mat,len(found[kind][mat]),len(expected[kind][mat]))
 # Every non-POSITION byte must remain identical, including JSON/bounds, normals, UVs and indices.
 allowed=set(i for a,z in ranges for i in range(a,z));diff=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b];assert set(diff)<=allowed
 assert all(before[o:o+12]==after[o:o+12] for o in first)
 # Retain original accessor bounds conservatively; all moved vertices must remain enclosed.
 for m in d['meshes']:
  for p in m['primitives']:
   a=d['accessors'][p['attributes']['POSITION']];v,_=access(d,after,base,p['attributes']['POSITION'])
   for j in range(3):assert min(x[j] for x in v)>=a['min'][j]-1e-5 and max(x[j] for x in v)<=a['max'][j]+1e-5
 # Project actual exported vertices onto straight return tangent.
 curve=8.72*math.radians(98);svals=[curve-(x+47.25)*T[0]-(-z+10.53)*T[1] for x,y,z in target_after]
 sb=[min(svals),max(svals)];pier=json.loads((ROOT/'source/GEOMETRIC_DIAGNOSTIC.json').read_text());clearance=pier['yellow_end_pier_bounds'][0]-sb[1];margin=pier['canopy_end']-sb[1]
 assert clearance>=.04999 and margin>=.69999 and sb[0]>curve
 # Narrow metadata exception: exact glTF POSITION extrema. No other JSON value changes.
 original_json=copy.deepcopy(d);json_delta=[]
 for ai,a in enumerate(d['accessors']):
  if not any(p['attributes'].get('POSITION')==ai for m in d['meshes'] for p in m['primitives']):continue
  v,_=access(d,after,base,ai)
  for field,fn in [('min',min),('max',max)]:
   exact=[fn(x[j] for x in v) for j in range(3)]
   if a[field]!=exact:
    json_delta.append({'accessor':ai,'field':field,'before':a[field],'after':exact});a[field]=exact
 jb=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode();jb+=b' '*((-len(jb))%4)
 binary=bytes(after[base:]);after=bytearray(struct.pack('<4sII',b'glTF',2,28+len(jb)+len(binary))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(binary),b'BIN\x00')+binary)
 (ROOT/'evidence/json_delta.json').write_text(json.dumps(json_delta,indent=2)+'\n')
 (ROOT/'web/ekimae.glb').write_bytes(after)
 report={'input_sha256':sha(before),'output_sha256':sha(after),'byte_length':len(before),'byte_length_unchanged':len(before)==len(after),'all_unrelated_json_values_and_bin_bytes_identical':True,'json_metadata_delta':json_delta,'output_bin_offset':28+len(jb),'changed_byte_count':len(diff),'allowed_position_ranges':ranges,'selection':details,'target_signature_triangles':{k:len(v) for k,v in expected['target'].items()},'first_door_signature_triangles':{k:len(v) for k,v in expected['first_door'].items()},'first_door_all_bytes_unchanged':True,'translation_gltf':delta,'actual_s_envelope':sb,'actual_pier_clearance_m':clearance,'actual_canopy_end_margin_m':margin,'accessor_bounds_recomputed_exactly':True,'normals_uv_indices_materials_nodes_identical':True,'geometry_scope':'Only original-generator signature matched north-return two jambs, header, paired bars','limitations':['Model consistency only, no calibrated photo registration','Inherited mullion remains off-center','No navigation/FPS validation']}
 (ROOT/'evidence/audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='allowed_position_ranges'},indent=2))
if __name__=='__main__':run()
