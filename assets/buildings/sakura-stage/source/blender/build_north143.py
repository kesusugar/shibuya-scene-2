"""Deterministic Sakura north143 replacement. Python3 stdlib, no terrain regeneration.
Run: python source/blender/build.py [output.glb]
Blender 4.2.3 render.py creates the packed editable scene from the identical GLB.
Baseline is immutable pinned 2026-10-14 main; no off-target primitive attributes changed.
"""
import json,struct,math,hashlib,sys,copy
from pathlib import Path
A=Path(__file__).resolve().parents[2]
BASE_SHA='0781a138445fa96b2f34a5491c0c238dbbd9af7f2d0fe7ae8536c59f3e7de98e'
E=(126.564,-230.614);W=(66.751,-263.078);WIDTH=math.dist(E,W);T=((W[0]-E[0])/WIDTH,(W[1]-E[1])/WIDTH);N=(T[1],-T[0]);Z0=25.1;Z1=180.843

def load(path):
 b=Path(path).read_bytes();ln=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+ln]);bl=struct.unpack_from('<I',b,20+ln)[0];return d,bytearray(b[28+ln:28+ln+bl])
def accessor(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3}[a['type']];fmt={5126:'f',5125:'I',5123:'H'}[a['componentType']];sz=struct.calcsize('<'+fmt*n);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',sz);return [struct.unpack_from('<'+fmt*n,b,off+j*stride) for j in range(a['count'])]
def source(p):return p[0],-p[2],p[1]
def coords(p):
 x,y,z=source(p);return ((x-E[0])*T[0]+(y-E[1])*T[1]),((x-E[0])*N[0]+(y-E[1])*N[1]),z
def target_triangle(positions,tri):
 vals=[coords(positions[i]) for i in tri]
 return all(-.002<=u<=WIDTH+.002 and .06<dep<.195 and Z0-.002<=z<=Z1+.002 for u,dep,z in vals) and max(x[1] for x in vals)-min(x[1] for x in vals)<.001

def append_accessor(d,b,rows,typ,ctype=5126):
 while len(b)%4:b.append(0)
 offset=len(b);fmt={5126:'f',5125:'I',5123:'H'}[ctype]
 for row in rows:b.extend(struct.pack('<'+fmt*len(row),*row))
 vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(b)-offset});ac={'bufferView':vi,'componentType':ctype,'count':len(rows),'type':typ}
 if typ=='VEC3':ac['min']=[min(r[i] for r in rows) for i in range(3)];ac['max']=[max(r[i] for r in rows) for i in range(3)]
 ai=len(d['accessors']);d['accessors'].append(ac);return ai

def write(d,b,path):
 while len(b)%4:b.append(0)
 d['buffers'][0]['byteLength']=len(b);j=json.dumps(d,separators=(',',':'),ensure_ascii=True).encode();j+=b' '*((-len(j))%4)
 Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b)

def main(output):
 source_path=A/'source/data/plateau.json'
 assert hashlib.sha256(source_path.read_bytes()).hexdigest()=='6a58d4643e44a4442b5cbc11cb0808f26c4c19b5eb7d5e05c5ef57b42ab9602e'
 ring=json.loads(source_path.read_text())['surfaces'][143]['ring']
 assert all(abs(((p[0]-E[0])*N[0]+(p[1]-E[1])*N[1]))<.001 for p in ring)
 assert abs(min(p[2] for p in ring)-Z0)<.001 and abs(max(p[2] for p in ring)-Z1)<.001
 baseline=A/'source/data/baseline.glb';assert hashlib.sha256(baseline.read_bytes()).hexdigest()==BASE_SHA
 d,b=load(baseline);original_materials=copy.deepcopy(d['materials']);removed={};kept=0
 for mesh in d['meshes']:
  for p in mesh['primitives']:
   ids=[v[0] for v in accessor(d,b,p['indices'])];pos=accessor(d,b,p['attributes']['POSITION']);new=[];nr=0
   for k in range(0,len(ids),3):
    tri=ids[k:k+3]
    if mesh['name'] not in ['sakura-stage_wall','sakura-stage_roof'] and target_triangle(pos,tri):nr+=1
    else:new.extend((i,) for i in tri)
   removed[mesh['name']]=nr;kept+=len(new)//3
   if nr:p['indices']=append_accessor(d,b,new,'SCALAR',5125)
 # Original vertex buffers are preserved, not re-exported; removed indices alone vanish.
 assert removed['sakura-stage_frame']>40
 groups={};features=[]
 def point(u,z,depth):return (E[0]+T[0]*u+N[0]*depth,z,-(E[1]+T[1]*u+N[1]*depth))
 def face(mat,points):
  points=list(reversed(points)) # outward front and shallow sides in glTF Y-up
  g=groups.setdefault(mat,{'p':[],'n':[],'i':[]});a,bp,c=points[:3];ab=[bp[i]-a[i] for i in range(3)];ac=[c[i]-a[i] for i in range(3)];cr=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];ln=math.sqrt(sum(x*x for x in cr));norm=tuple(x/ln for x in cr);base=len(g['p']);g['p']+=points;g['n']+=[norm]*len(points)
  for i in range(1,len(points)-1):g['i'] += [(base,),(base+i,),(base+i+1,)]
 def quad(mat,u0,u1,z0,z1,dep=.08):face(mat,[point(u0,z0,dep),point(u0,z1,dep),point(u1,z1,dep),point(u1,z0,dep)])
 def box(mat,u0,u1,z0,z1,back=.1,front=.34):
  # Front plus four shallow side faces; rear lies against facade, no duplicated shell.
  a=[point(u0,z0,back),point(u0,z1,back),point(u1,z1,back),point(u1,z0,back)];c=[point(u0,z0,front),point(u0,z1,front),point(u1,z1,front),point(u1,z0,front)];face(mat,c)
  for i in range(4):j=(i+1)%4;face(mat,[a[i],a[j],c[j],c[i]])
 def record(kind,**kw):features.append(dict(surface=143,kind=kind,**kw))
 def material(name,rgb,metal,rough):
  idx=len(d['materials']);d['materials'].append({'name':'sakura-stage_north143_'+name,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[*rgb,1],'metallicFactor':metal,'roughnessFactor':rough}});return idx
 glass=material('glass',(.12,.21,.28),.3,.30);spandrel=material('spandrel',(.32,.40,.44),.3,.55);fin=material('fins',(.66,.70,.71),.50,.40);dark=material('dark_glass',(.025,.043,.057),.3,.30)
 # Photo interpretation: 40 narrow bays, two dark panes at bays17/18 (q.425-.475).
 # Width/count/depth and floor levels estimated, not a measured architectural survey.
 cols=40;pitch=WIDTH/cols;step=(183.603/39);floorbase=-2.76
 # Keep source silhouette and podium below25.1 exactly untouched.
 quad(glass,.025,WIDTH-.025,Z0+.02,Z1-.03,.075)
 # Replace 0.095m token strips with1.05m opaque bands, individual dark panes segmented.
 for row in range(6,39):
  lo=max(Z0+.03,floorbase+row*step);hi=min(Z1-.04,floorbase+(row+1)*step)
  if hi<=lo:continue
  band=min(1.05,(hi-lo)*.30);quad(spandrel,.03,WIDTH-.03,lo,lo+band,.105)
  # Narrow two-pane stripe, not a shell cutout, floor spandrels remain visible.
  for col in (17,18):quad(dark,col*pitch+.10,(col+1)*pitch-.10,lo+band,hi-.10,.115)
 record('segmented_dark_stripe',q=[17/40,19/40],pane_count=2,z=[Z0,Z1],basis='February and September2025 visual proportions; approximate')
 for col in range(cols+1):
  u=col*pitch;box(fin,max(.02,u-.065),min(WIDTH-.02,u+.065),Z0+.03,Z1-.04,.11,.34)
 record('continuous_fins',count=41,pitch_m=pitch,width_m=.13,depth_m=.34,z=[Z0+.03,Z1-.04])
 record('spandrels',height_m=1.05,storey_pitch_m=step,first_row=6,last_row=38)
 # Stronger pair approximately 60% and66% up the visible source143 height.
 # Photos support pair and relative heights, not surveyed dimensions.
 for z in (118.5,127.9):
  box(fin,.03,WIDTH-.03,z,z+.30,.12,.42);quad(dark,.04,WIDTH-.04,z-.18,z,.12)
 record('strong_horizontal_belts',bottom_z_m=[118.5,127.9],height_m=.30,depth_m=.42)
 quad(dark,.08,WIDTH-.08,173.5,177.1,.12)
 # Roof dark glazing is behind continuing fins, not new rooftop or parapet geometry.
 record('roof_level_dark_strip',z=[173.5,177.1],depth_m=.12)
 for mat,g in groups.items():
  pi=append_accessor(d,b,g['p'],'VEC3');ni=append_accessor(d,b,g['n'],'VEC3');ii=append_accessor(d,b,g['i'],'SCALAR',5125);mi=len(d['meshes']);name=d['materials'][mat]['name'];d['meshes'].append({'name':name,'primitives':[{'attributes':{'POSITION':pi,'NORMAL':ni},'indices':ii,'material':mat}]});node=len(d['nodes']);d['nodes'].append({'name':name,'mesh':mi});d['scenes'][d.get('scene',0)]['nodes'].append(node)
 assert d['materials'][:len(original_materials)]==original_materials
 write(d,b,output);counts={'triangles':kept+sum(len(g['i'])//3 for g in groups.values()),'primitives':sum(len(m['primitives']) for m in d['meshes']),'bytes':Path(output).stat().st_size};assert counts['triangles']<=120000 and counts['primitives']<=40 and counts['bytes']<=3000000,counts
 report={'baseline_sha256':BASE_SHA,'surface':143,'q0':'east endpoint; photo-left','east_endpoint':E,'west_endpoint':W,'width_m':WIDTH,'removed_triangles':removed,'features':features,'stats':counts,'inherited_zero_area_wall_triangles':8,'preserved':'all shell/roof, footing, source rings, off-target triangle attributes and materials;306 pavement samples','limits':'asset-local studio only; no full-scene/nighttime/FPS certification; no October-specific evidence'}
 Path(output).with_suffix('.north143.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else A/'web/sakura-stage.glb')
