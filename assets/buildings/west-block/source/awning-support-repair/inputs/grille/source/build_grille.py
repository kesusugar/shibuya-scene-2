"""Deterministic append-only glTF successor. No Blender round-trip of accepted geometry."""
import json, struct, math, hashlib, shutil, argparse
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes(); assert b[:4]==b'glTF'; n=struct.unpack_from('<I',b,12)[0]; j=json.loads(b[20:20+n]); size,typ=struct.unpack_from('<II',b,20+n); assert typ==0x004e4942
 return j,b[28+n:28+n+size]
def write(p,j,b):
 b+=b'\0'*((-len(b))%4);j['buffers'][0]['byteLength']=len(b); s=json.dumps(j,separators=(',',':'),ensure_ascii=True).encode();s+=b' '*((-len(s))%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(s)+len(b))+struct.pack('<II',len(s),0x4e4f534a)+s+struct.pack('<II',len(b),0x004e4942)+b)
def main(root):
 for pin in json.loads((root/'INPUT_PINS.json').read_text()): assert sha(root/pin['path'])==pin['sha256'],pin['path']
 base,old=read(root/'inputs/web/west-block.glb');j=json.loads(json.dumps(base)); binary=bytearray(old); groups=[([],[],[]),([],[],[])]; parts=[]
 t=(.993768268,.111465822);n=(.111465822,-.993768268)
 def world(u,d,z): return (-49+u*t[0]+d*n[0],z,-(23.326344151+u*t[1]+d*n[1]))
 def box(name,u,d,z,w,depth,h,mat=0,tilt=0):
  pos,norm,ind=groups[mat];a=math.radians(tilt); vertices=[]
  for x,y,q in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
   dy=y*depth/2;dz=q*h/2;vertices.append(world(u+x*w/2,d+dy*math.cos(a)-dz*math.sin(a),z+dy*math.sin(a)+dz*math.cos(a)))
  cen=world(u,d,z)
  for face in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
   v=[vertices[i] for i in face];e=[v[1][k]-v[0][k] for k in range(3)];f=[v[2][k]-v[0][k] for k in range(3)];normal=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]]
   if sum(normal[k]*(v[0][k]-cen[k]) for k in range(3))<0: v.reverse();normal=[-x for x in normal]
   mag=math.sqrt(sum(x*x for x in normal));normal=[x/mag for x in normal];start=len(pos);pos.extend(v);norm.extend([normal]*4);ind.extend([start,start+1,start+2,start,start+2,start+3])
  parts.append(dict(name=name,center_ud_z=[u,d,z],size=[w,depth,h],tilt=tilt,material=mat))
 for z in [3.2925,3.8375]:box('outer_horizontal',0,.32,z,2.83,.16,.035)
 for u in [-1.3975,1.3975]:box('outer_vertical',u,.32,3.565,.035,.16,.51)
 clear=(2.83-.07-5*.028)/6
 for k in range(5):box('separator_'+str(k+1),-1.38+(k+1)*clear+k*.028+.014,.32,3.565,.028,.16,.51)
 for cell in range(6):
  u=-1.38+clear/2+cell*(clear+.028)
  box('recess_'+str(cell+1),u,.25,3.565,clear,.016,.51,1)
  if cell in [0,1,4,5]:
   for b in range(5):box('blade_%d_%d'%(cell+1,b+1),u,.342,3.565+(b-2)*.085,clear,.075,.025,0,-15)
  else:
   for b in range(4):box('fine_grille_%d_%d'%(cell+1,b+1),u,.278,3.565+(b-1.5)*.10,clear,.015,.012,1)
 def accessor(values,kind,typ,target):
  width={'VEC3':3,'SCALAR':1}[typ];flat=[x for v in values for x in v] if width>1 else values;code='f' if kind==5126 else 'H'
  binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);data=struct.pack('<'+code*len(flat),*flat);binary.extend(data);vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=len(data),target=target)); ai=len(j['accessors']);entry=dict(bufferView=vi,componentType=kind,count=len(values),type=typ)
  if typ=='VEC3':entry.update(min=[min(v[k] for v in values) for k in range(3)],max=[max(v[k] for v in values) for k in range(3)])
  j['accessors'].append(entry);return ai
 metal=next(i for i,m in enumerate(j['materials']) if m['name']=='west_metal_edge');dark=len(j['materials']);j['materials'].append(dict(name='west_grille_recess',pbrMetallicRoughness=dict(baseColorFactor=[.065,.075,.07,1],metallicFactor=.25,roughnessFactor=.8)))
 prim=[]
 for g,mat in zip(groups,[metal,dark]):
  p,no,ix=g;prim.append(dict(attributes={'POSITION':accessor(p,5126,'VEC3',34962),'NORMAL':accessor(no,5126,'VEC3',34962)},indices=accessor(ix,5123,'SCALAR',34963),material=mat,mode=4))
 mesh=len(j['meshes']);j['meshes'].append(dict(name='west_six_cell_grille_apron',primitives=prim));node=len(j['nodes']);j['nodes'].append(dict(name='west_six_cell_grille_apron',mesh=mesh));j['scenes'][j.get('scene',0)]['nodes'].append(node)
 out=root/'web';out.mkdir(exist_ok=True);write(out/'west-block.glb',j,bytes(binary))
 for name in ['signs-2025-01.glb','viewer.json']:shutil.copyfile(root/'inputs/web'/name,out/name)
 (root/'evidence/parts.json').write_text(json.dumps(parts,indent=2)+'\n')
 after,ab=read(out/'west-block.glb'); assert ab[:len(old)]==old
 for key in base:
  if key in ['buffers','scenes']:continue
  if isinstance(base[key],list):assert after[key][:len(base[key])]==base[key],key
  else:assert after[key]==base[key],key
 assert after['scenes'][0]['nodes'][:-1]==base['scenes'][0]['nodes']
 def stats(j):return {'triangles':sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives']),'primitives':sum(len(m['primitives']) for m in j['meshes'])}
 sign,_=read(out/'signs-2025-01.glb');bs,ss,ns=stats(base),stats(sign),stats(after);total={k:ns[k]+ss[k] for k in ns};total['bytes']=sum((out/n).stat().st_size for n in ['west-block.glb','signs-2025-01.glb']);assert ns['triangles']-bs['triangles']<=600;assert ns['primitives']-bs['primitives']<=2;assert total['triangles']<=120000 and total['primitives']<=40 and total['bytes']<=3000000
 report={'before_base':bs,'after_base':ns,'unchanged_sign_layer':ss,'combined':total,'added_triangles':ns['triangles']-bs['triangles'],'added_primitives':2,'original_binary_prefix_exact':True,'all_original_json_array_entries_exact':True,'sign_bytes_exact':sha(out/'signs-2025-01.glb')==sha(root/'inputs/web/signs-2025-01.glb'),'viewer_bytes_exact':sha(out/'viewer.json')==sha(root/'inputs/web/viewer.json'),'output_sha256':{n:sha(out/n) for n in ['west-block.glb','signs-2025-01.glb','viewer.json']}}
 (root/'evidence/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);main(ap.parse_args().root)
