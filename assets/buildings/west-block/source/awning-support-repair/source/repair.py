"""Narrow binary patch; Python standard library only. Never round-trip original GLB."""
import json,struct,hashlib,math,shutil,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def unit(v):
 l=math.sqrt(sum(x*x for x in v));assert l>1e-12;return [x/l for x in v]
def main(root):
 pin=json.loads((root/'source/SUPPORT_TARGET.json').read_text());src=(root/'inputs/current/west-block.glb').read_bytes();assert sha(src)==pin['base_sha256'];out=bytearray(src)
 n=struct.unpack_from('<I',src,12)[0];j=json.loads(src[20:20+n]);bo=28+n
 def offset(ai,v=0):
  a=j['accessors'][ai];bv=j['bufferViews'][a['bufferView']];width={'VEC3':12,'SCALAR':{5123:2,5125:4}[a['componentType']] if a['type']=='SCALAR' else 0}[a['type']]
  return bo+bv.get('byteOffset',0)+a.get('byteOffset',0)+v*bv.get('byteStride',width)
 def vec(ai,v,b=src):return struct.unpack_from('<3f',b,offset(ai,v))
 t=pin['targets'][0];pa,na,ia=[t[k] for k in ['position_accessor','normal_accessor','index_accessor']];pr=j['meshes'][12]['primitives'][0];assert pr['attributes']['POSITION']==pa and pr['attributes']['NORMAL']==na and pr['indices']==ia
 acc=j['accessors'][ia];indices=struct.unpack_from('<'+('H' if acc['componentType']==5123 else 'I')*acc['count'],src,offset(ia));tri=[indices[i:i+3] for i in range(0,len(indices),3)];ids=set(t['vertex_indices']);tris=set(t['triangle_indices']);assert len(ids)==48 and len(tris)==24
 assert set(v for q in tris for v in tri[q])==ids;assert not any(v in ids for q,tr in enumerate(tri) if q not in tris for v in tr)
 # Accessors must be exclusive to this primitive, so no hidden aliasing across primitives.
 assert sum(p['attributes'].get('POSITION')==pa for m in j['meshes'] for p in m['primitives'])==1
 assert sum(p['attributes'].get('NORMAL')==na for m in j['meshes'] for p in m['primitives'])==1
 C=pin['coordinate_basis']['C'];nx,ny,_=pin['coordinate_basis']['n'];k=.53/1.65;allowed=[];clear=[]
 for v in sorted(ids):
  x,z,my=vec(pa,v);d=(x-C[0])*nx+(-my-C[1])*ny;zz=z-3.05+3.35-k*d-.07
  struct.pack_into('<f',out,offset(pa,v)+4,zz);allowed.append([offset(pa,v)+4,offset(pa,v)+8])
  norm=vec(na,v);new=unit([norm[0]+k*nx*norm[1],norm[1],norm[2]-k*ny*norm[1]])
  struct.pack_into('<3f',out,offset(na,v),*new);allowed.append([offset(na,v),offset(na,v)+12])
  actual=vec(pa,v,out);assert actual[0]==x and actual[2]==my
  assert abs(actual[1]-(3.35-k*d-.07)-(z-3.05))<2e-7
  if z>3.05:clear.append(3.35-k*d-actual[1])
 dot=[]
 for q in tris:
  vs=[vec(pa,v,out) for v in tri[q]];e=[vs[1][k]-vs[0][k] for k in range(3)];f=[vs[2][k]-vs[0][k] for k in range(3)];normal=unit([e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]])
  for v in tri[q]:dot.append(sum(a*b for a,b in zip(normal,vec(na,v,out))))
 assert min(dot)>.999999;assert max(abs(c-.025) for c in clear)<2e-7
 permit=set(i for a,b in allowed for i in range(a,b));changed=[i for i,(a,b) in enumerate(zip(src,out)) if a!=b];assert all(i in permit for i in changed);assert len(out)==len(src)
 (root/'web').mkdir(exist_ok=True);(root/'web/west-block.glb').write_bytes(out)
 companions={}
 for f,h in [('signs-2025-01.glb','dbd49d4aca93e123daf1f9225b2eec48d0e6f7be383e5c7827cd35405c039386'),('viewer.json','6bf813d79c29d9a5d5287705028a662f8a8a1bfed8c96156469037b122aca5fd')]:
  b=(root/'inputs/current'/f).read_bytes();assert sha(b)==h;shutil.copyfile(root/'inputs/current'/f,root/'web'/f);companions[f]=h
 report=dict(base_sha256=sha(src),output_sha256=sha(out),triangles=24,vertices=48,changed_bytes=len(changed),allowed_byte_ranges=sorted(allowed),outside_allowed_bytes_exact=True,json_chunk_exact=True,topology_material_uv_grille_exact=True,normal_winding_min_dot=min(dot),clearance_m=[min(clear),max(clear)],clearance_status='25mm inferred modeling tolerance, not surveyed',companions_sha256=companions)
 (root/'evidence').mkdir(exist_ok=True);(root/'evidence/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='allowed_byte_ranges'},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);main(p.parse_args().root)
