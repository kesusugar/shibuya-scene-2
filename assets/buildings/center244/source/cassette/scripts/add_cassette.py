"""Deterministic binary-prefix-preserving GLB append. Python standard library only."""
import json,struct,hashlib,copy,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read_glb(p):
 b=Path(p).read_bytes();magic,v,total=struct.unpack_from('<4sII',b);assert magic==b'glTF' and v==2 and total==len(b)
 n,typ=struct.unpack_from('<II',b,12);assert typ==0x4e4f534a;j=json.loads(b[20:20+n]);k=20+n;m,typ=struct.unpack_from('<II',b,k);assert typ==0x004e4942 and k+8+m==len(b)
 return j,b[k+8:k+8+m]
def write_glb(p,j,b):
 jb=json.dumps(j,separators=(',',':'),ensure_ascii=False).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4)
 Path(p).write_bytes(struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(b),0x004e4942)+b)
def specs(q):
 u0,u1=q['local_bounds']['u'];return [('top_housing',(u0,u1,.055,.30,4.645,4.70),0),('left_cap',(u0,u0+.07,.055,.30,4.43,4.645),0),('right_cap',(u1-.07,u1,.055,.30,4.43,4.645),0),('recess_slot',(u0+.07,u1-.07,.265,.28,4.59,4.625),1)]
def geometry(q):
 # Local (u,d,z) is left handed; map to glTF first then derive each outward normal.
 groups=[([],[],[]),([],[],[])];components=[]
 for name,box,mat in specs(q):
  a,b,c,d,e,f=box;local=[(a,c,e),(b,c,e),(b,d,e),(a,d,e),(a,c,f),(b,c,f),(b,d,f),(a,d,f)]
  verts=[]
  for u,dep,z in local:
   x=q['origin_a'][0]+u*q['tangent'][0]+dep*q['outward'][0];y=q['origin_a'][1]+u*q['tangent'][1]+dep*q['outward'][1];verts.append((x,z,-y))
  # outward winding in left-handed local coordinates
  faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
  P,N,I=groups[mat];start=len(P)
  for face in faces:
   v=[verts[i] for i in face];ab=[v[1][i]-v[0][i] for i in range(3)];ac=[v[2][i]-v[0][i] for i in range(3)];n=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];length=sum(x*x for x in n)**.5;n=[x/length for x in n];offset=len(P);P.extend(v);N.extend([n]*4);I.extend(offset+i for i in [0,1,2,0,2,3])
  components.append({'name':name,'bounds_ud_z':box,'material_group':mat,'vertex_start':start,'vertex_count':24,'triangles':12})
 return groups,components
def build(out):
 pins=json.loads((ROOT/'inputs/PINS.json').read_text())
 for name,h in pins.items():assert hashlib.sha256((ROOT/'inputs'/name).read_bytes()).hexdigest()==h,name
 j,old=read_glb(ROOT/'inputs/center244.glb');q=json.loads((ROOT/'inputs/PROPOSAL.json').read_text());binary=bytearray(old);groups,components=geometry(q);m0=len(j['materials'])
 for name,color,metal,rough in [('c244_cassette_pale_metal',[.72,.74,.73,1],.5,.38),('c244_cassette_dark_recess',[.045,.05,.048,1],.15,.68)]:j['materials'].append({'name':name,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':metal,'roughnessFactor':rough},'doubleSided':False})
 def accessor(vals,fmt,ct,typ,target):
  binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);flat=[x for v in vals for x in v] if typ=='VEC3' else vals;data=struct.pack('<'+str(len(flat))+fmt,*flat);binary.extend(data);vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':target});a={'bufferView':vi,'componentType':ct,'count':len(vals),'type':typ}
  if typ=='VEC3':a.update(min=[min(v[k] for v in vals) for k in range(3)],max=[max(v[k] for v in vals) for k in range(3)])
  ix=len(j['accessors']);j['accessors'].append(a);return ix
 prim=[]
 for i,(p,n,idx) in enumerate(groups):prim.append({'attributes':{'POSITION':accessor(p,'f',5126,'VEC3',34962),'NORMAL':accessor(n,'f',5126,'VEC3',34962)},'indices':accessor(idx,'H',5123,'SCALAR',34963),'material':m0+i,'mode':4})
 mesh=len(j['meshes']);j['meshes'].append({'name':'c244_chamfer_cassette','primitives':prim});node=len(j['nodes']);j['nodes'].append({'mesh':mesh,'name':'c244_chamfer_cassette'});j['scenes'][j.get('scene',0)]['nodes'].append(node);j['buffers'][0]['byteLength']=len(binary)
 out.mkdir(parents=True,exist_ok=True);write_glb(out/'center244.glb',j,bytes(binary));(out/'components.json').write_text(json.dumps(components,indent=2)+'\n');print(hashlib.sha256((out/'center244.glb').read_bytes()).hexdigest())
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'output');args=ap.parse_args();build(args.out)
