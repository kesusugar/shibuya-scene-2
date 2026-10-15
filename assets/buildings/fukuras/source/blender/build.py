"""Blender 4.2.3 asset-local Fukuras overlay. No resampling or translation.
Run: blender -b --python-exit-code 1 -P .../build.py
Baseline is exact main275f832. Wall74/76/81 tessellation is repaired; roof35 only is additionally repaired; all off-target geometry is preserved.
"""
import bpy,json,struct,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
assert bpy.app.version[:3]==(4,2,3),bpy.app.version_string
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'source/data'; OUT=ROOT/'web'
D=json.loads((DATA/'plateau.json').read_text()); raw=(DATA/'baseline.glb').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e25a48ed0f4792088de9e5dfed71db2249e5a7b95f71b9d7cf866bde6a8069bb'
n=struct.unpack_from('<I',raw,12)[0]; doc=json.loads(raw[20:20+n]); binary=bytearray(raw[28+n:]); mask=[76,81,135]; records=[]
def accessor(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];size={'SCALAR':1,'VEC3':3}[a['type']];fmt={5123:'H',5125:'I',5126:'f'}[a['componentType']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',struct.calcsize(fmt)*size)
 return [struct.unpack_from('<'+fmt*size,binary,start+k*stride) for k in range(a['count'])]
def add_accessor(rows,typ='VEC3',ctype=5126):
 while len(binary)%4:binary.append(0)
 start=len(binary);fmt={5125:'I',5126:'f'}[ctype];width=3 if typ=='VEC3' else 1
 for row in rows:binary.extend(struct.pack('<'+fmt*width,*row))
 v=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':len(binary)-start})
 a={'bufferView':v,'componentType':ctype,'count':len(rows),'type':typ}
 if typ=='VEC3':a.update(min=[min(p[k] for p in rows) for k in range(3)],max=[max(p[k] for p in rows) for k in range(3)])
 doc['accessors'].append(a);return len(doc['accessors'])-1
faces={}
for si in mask:
 ring=[Vector(p) for p in D['surfaces'][si]['ring'][:-1]];o=ring[0];norm=Vector((-.393,.920,0)) if si==76 else Vector((.920,.393,0)) if si==81 else Vector((.300,.954,0));norm.normalize();t=Vector((norm.y,-norm.x,0));poly=[Vector(((p-o).dot(t),p.z,0)) for p in ring];tris=tessellate_polygon([poly]);tris=[[poly[x] for x in tr] if isinstance(tr[0],int) else tr for tr in tris]
 # Obtain exact horizontal plane normal from edge directions; chosen sign is exterior.
 nn=Vector((0,0,0))
 for i,p in enumerate(ring):
  q=ring[i-1];nn.x+=(p.y-q.y)*(p.z+q.z);nn.y+=(p.z-q.z)*(p.x+q.x);nn.z+=(p.x-q.x)*(p.y+q.y)
 nn.normalize();norm=nn if nn.dot(norm)>0 else -nn;t=Vector((norm.y,-norm.x,0));poly=[Vector(((p-o).dot(t),p.z,0)) for p in ring];tris=tessellate_polygon([poly]);tris=[[poly[x] for x in tr] if isinstance(tr[0],int) else tr for tr in tris]
 faces[si]=(o,norm,t,poly,tris)
def inside(p,poly):
 x,y=p;flag=False
 for i,a in enumerate(poly):
  b=poly[i-1]
  if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:flag=not flag
 return flag
removed={}
for mesh in doc['meshes']:
 for p in mesh['primitives']:
  name=doc['materials'][p['material']]['name']
  if name in ['fukuras_wall','fukuras_roof']:continue
  verts=[Vector((v[0],-v[2],v[1])) for v in accessor(p['attributes']['POSITION'])];idx=[v[0] for v in accessor(p['indices'])];keep=[]
  for k in range(0,len(idx),3):
   ix=idx[k:k+3];vs=[verts[i] for i in ix];c=sum(vs,Vector())/3;hit=False
   for si,(o,n,t,poly,tris) in faces.items():
    depth=(c-o).dot(n)
    if c.z<=83.9 and .035<depth<.25 and all(abs((v-c).dot(n))<.008 for v in vs) and inside(((c-o).dot(t),c.z),poly):hit=True;removed[si]=removed.get(si,0)+1;break
   if not hit:keep.extend((i,) for i in ix)
  p['indices']=add_accessor(keep,'SCALAR',5125)
# New merged material primitives, all facade pieces offset from original shell.
geo={}; counts={}; mats={}
for name,rgb,metal,rough in [('curtain_glass',[.075,.145,.19],.3,.26),('infill_silver',[.44,.49,.51],.65,.35),('mullion_silver',[.32,.38,.40],.7,.3),('circulation_glass',[.025,.055,.064],.25,.3),('circulation_metal',[.25,.29,.28],.55,.42)]:
 mats[name]=len(doc['materials']);doc['materials'].append({'name':'fukuras_'+name,'pbrMetallicRoughness':{'baseColorFactor':rgb+[1],'metallicFactor':metal,'roughnessFactor':rough},'doubleSided':False})
def clip(subject,triangle):
 tri=[(v.x,v.y) for v in triangle];area=sum(tri[i-1][0]*tri[i][1]-tri[i][0]*tri[i-1][1] for i in range(3));sgn=1 if area>0 else -1
 for i,a in enumerate(tri):
  b=tri[(i+1)%3];out=[]
  def side(p):return sgn*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
  if not subject:break
  prev=subject[-1];sp=side(prev)
  for curr in subject:
   sc=side(curr)
   if (sc>=-1e-8)!=(sp>=-1e-8):
    f=sp/(sp-sc);out.append((prev[0]+f*(curr[0]-prev[0]),prev[1]+f*(curr[1]-prev[1])))
   if sc>=-1e-8:out.append(curr)
   prev=curr;sp=sc
  subject=out
 return subject
def shape(si,points,mat,depth):
 o,n,t,poly,tris=faces[si];vs,ns,ix=geo.setdefault(mat,([],[],[]));initial=len(ix)
 for tr in tris:
  clipped=clip(points,tr)
  if len(clipped)<3:continue
  area=sum(clipped[i-1][0]*clipped[i][1]-clipped[i][0]*clipped[i-1][1] for i in range(len(clipped)))
  # t cross up is -normal: reverse positive UV winding.
  if area>0:clipped.reverse()
  if abs(area)<1e-7:continue
  start=len(vs)
  for u,z in clipped:
   p=o+t*u+n*depth;p.z=z;vs.append((p.x,p.z,-p.y));ns.append((n.x,n.z,-n.y))
  for j in range(1,len(clipped)-1):
   a,b,c=clipped[0],clipped[j],clipped[j+1]
   if abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))>1e-5:ix.extend([(start,),(start+j,),(start+j+1,)])
 if len(ix)==initial:return
 counts[(si,mat)]=counts.get((si,mat),0)+1
 records.append({'surface':si,'material':mat,'depth_m':depth,'uv':points})
def rect(si,u0,u1,z0,z1,mat,depth):
 if u1>u0 and z1>z0:shape(si,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)],mat,depth)
# Explicit grouped patches: normalized horizontal extents and absolute source-z intervals.
patches={76:[(.04,.17,45.3,48.3),(.21,.43,51.2,54.2),(.45,.61,54.2,57.2),(.68,.85,45.3,48.3),(.08,.25,63.1,66.1),(.25,.36,66.1,69.1),(.48,.69,69.1,72.1),(.71,.91,57.2,60.2),(.33,.49,77.9,80.9),(.75,.96,75,78)],81:[(.06,.28,45.3,48.3),(.35,.56,54.2,57.2),(.62,.83,48.3,51.3),(.14,.34,66.1,69.1),(.40,.63,72,75),(.72,.94,63.1,66.1),(.11,.29,78,81)],135:[]}
for si,(o,n,t,poly,tris) in faces.items():
 lo=min(v.x for v in poly);hi=max(v.x for v in poly);width=hi-lo
 # Background infill and fine continuous curtain field; no heavy repeated floor strip.
 rect(si,lo,hi,42.3,83.9,'mullion_silver',.065)
 cols=max(1,round(width/1.8));pitch=width/cols;levels=[42.3,45.3,48.3,51.2,54.2,57.2,60.2,63.1,66.1,69.1,72.1,75,78,80.95,83.9]
 for col in range(cols):
  a=lo+col*pitch;b=a+pitch
  for z0,z1 in zip(levels,levels[1:]):
   infill=any(aa<((a+b)/2-lo)/width<bb and zz0<(z0+z1)/2<zz1 for aa,bb,zz0,zz1 in patches[si])
   rect(si,a+.045,b-.045,z0+.045,z1-.045,'infill_silver' if infill else 'curtain_glass',.132 if infill else .105)
 # Main lower urban-core volume, with a local broad transition cap.
 rect(si,lo,hi,1.31,40.0,'circulation_glass',.08)
 rect(si,lo,hi,40.0,42.3,'infill_silver',.205)
 # Corner is high-u on76, low-u on81. Broad returns do NOT cross tall corner glazing.
 corner_min=hi-min(18,width) if si==76 else lo;corner_max=hi if si==76 else lo+min(18,width)
 for z in [11.8,22.0,32.2]:
  if si==76:rect(si,lo,corner_min,z,z+3.1,'infill_silver',.205)
  elif si==81:rect(si,corner_max,hi,z,z+3.1,'infill_silver',.205)
 # Slender vertical subdivision with restrained transoms, tall not office-grid.
 for k in range(cols+1):
  u=lo+k*pitch;rect(si,u-.045,u+.045,1.31,40.0,'mullion_silver',.23)
 for z in [7.5,14.2,20.9,27.6,34.3]:rect(si,lo,hi,z,z+.065,'mullion_silver',.225)
 # Two bounded circulation relief elements, not a surveyed stair/interior count.
 # Paired stringer/handrail sections and balustrade posts are layered behind mullions.
 if si==81:
  a=lo+2.5;b=lo+13.5
  for z,rise in [(10,6),(22,-6)]:
   shape(si,[(a,z),(b,z+rise),(b,z+rise+.65),(a,z+.65)],'circulation_metal',.16)
   shape(si,[(a,z+1.45),(b,z+rise+1.45),(b,z+rise+1.55),(a,z+1.55)],'infill_silver',.19)
   shape(si,[(a,z+.56),(b,z+rise+.56),(b,z+rise+.64),(a,z+.64)],'infill_silver',.195)
   for j in range(9):
    u=a+(b-a)*j/8;zz=z+rise*j/8
    rect(si,u-.035,u+.035,zz+.65,zz+1.5,'circulation_metal',.18)
   for u,zz in [(a,z),(b,z+rise)]:rect(si,u-.55,u+.55,zz,zz+.24,'infill_silver',.20)
 for u in [lo,hi]:rect(si,u-.065,u+.065,1.31,83.9,'infill_silver',.25)
# Close each outward-offset corner joint with a narrow silver return, not a rounded podium.
for left,right,xy in [(76,135,(-14.848,-168.412)),(135,81,(-13.133,-168.950))]:
 ps=[];avg=Vector((0,0,0))
 for si in [left,right]:
  o,n,t,poly,tris=faces[si];p=Vector((*xy,1.31));u=(p-o).dot(t);q=o+t*u+n*.25;q.z=1.31;ps.append(q);avg+=n
 world=[ps[0],ps[1],ps[1]+Vector((0,0,82.59)),ps[0]+Vector((0,0,82.59))]
 if (world[1]-world[0]).cross(world[2]-world[0]).dot(avg)<0:world.reverse()
 pts=[Vector((p.x,p.z,-p.y)) for p in world];nn=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized();vv,ns,ix=geo['infill_silver'];st=len(vv);vv.extend(tuple(p) for p in pts);ns.extend([tuple(nn)]*4);ix.extend((st+i,) for i in [0,1,2,0,2,3])
# The side walls of circulation stringers make physical shallow relief, rather than painted diagonal lines.
o,n,t,poly,tris=faces[81]
lo=min(v.x for v in poly)
for z,rise in [(10,6),(22,-6)]:
 path=[(lo+2.5,z),(lo+13.5,z+rise),(lo+13.5,z+rise+.65),(lo+2.5,z+.65)]
 for j in range(4):
  a,b=path[j],path[(j+1)%4];ps=[]
  for uv,dep in [(a,.10),(b,.10),(b,.16),(a,.16)]:
   q=o+t*uv[0]+n*dep;q.z=uv[1];ps.append(Vector((q.x,q.z,-q.y)))
  nn=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized();vv,ns,ix=geo['circulation_metal'];st=len(vv);vv.extend(tuple(p) for p in ps);ns.extend([tuple(nn)]*4);ix.extend((st+i,) for i in [0,1,2,0,2,3])
for mat,(verts,normals,indices) in geo.items():
 verts=[struct.unpack('<fff',struct.pack('<fff',*v)) for v in verts]
 valid=[]
 for k in range(0,len(indices),3):
  ids=[r[0] for r in indices[k:k+3]];a,b,c=[Vector(verts[i]) for i in ids]
  if (b-a).cross(c-a).dot(Vector(normals[ids[0]]))>1e-7:valid.extend(indices[k:k+3])
 indices=valid
 prim={'attributes':{'POSITION':add_accessor(verts),'NORMAL':add_accessor(normals)},'indices':add_accessor(indices,'SCALAR',5125),'material':mats[mat]};mi=len(doc['meshes']);doc['meshes'].append({'name':'fukuras_'+mat,'primitives':[prim]});ni=len(doc['nodes']);doc['nodes'].append({'name':'fukuras_'+mat,'mesh':mi});doc['scenes'][doc.get('scene',0)]['nodes'].append(ni)
# Version2: repair ONLY the proven invalid triangle fans of source walls76/81.
# Keep every old buffer byte; append corrected local tessellation using the exact old
# boundary coordinates. No overlay changes, no roof changes, no resampling/translation.
tessellation_report=[]
for mesh in doc['meshes']:
 for primitive in mesh['primitives']:
  if doc['materials'][primitive['material']]['name']!='fukuras_wall':continue
  old_positions=accessor(primitive['attributes']['POSITION']);old_normals=accessor(primitive['attributes']['NORMAL']);old_indices=[v[0] for v in accessor(primitive['indices'])]
  old_world=[Vector((x,-z,y)) for x,y,z in old_positions];retained=[];owned={76:[],81:[]};source_rings={si:[Vector(p) for p in D['surfaces'][si]['ring'][:-1]] for si in [76,81]}
  for ti in range(0,len(old_indices),3):
   ids=old_indices[ti:ti+3];world=[old_world[i] for i in ids];target=None
   for si,ring in source_rings.items():
    if not all(min((p-v).length for v in ring)<.0003 for p in world):continue
    owners=[j for j,surface in enumerate(D['surfaces']) if all(min((p-Vector(v)).length for v in surface['ring'])<.0003 for p in world)]
    assert owners==[si],('Ambiguous source ownership',ti//3,owners)
    assert target is None
    target=si
   if target is None:retained.extend((i,) for i in ids)
   else:owned[target].append({'triangle_index':ti//3,'indices':ids})
  new_positions=list(old_positions);new_normals=list(old_normals)
  for si,ring in source_rings.items():
   assert len(owned[si])==len(ring)-2,(si,len(owned[si]),len(ring))
   o,n,t,poly,unused=faces[si]
   uv=[Vector(((p-o).dot(t),p.z,0)) for p in ring]
   triangles=tessellate_polygon([uv]);mapped=[]
   for triangle in triangles:
    ids=list(triangle) if isinstance(triangle[0],int) else [min(range(len(uv)),key=lambda j:(uv[j]-v).length) for v in triangle]
    mapped.append(ids)
   assert len(mapped)==len(ring)-2
   exact=[]
   for point in ring:
    ids=[i for rec in owned[si] for i in rec['indices'] if (old_world[i]-point).length<.0003]
    assert ids;exact.append(old_world[ids[0]].copy())
   for ids in mapped:
    points=[exact[i] for i in ids]
    normal=(points[1]-points[0]).cross(points[2]-points[0])
    assert normal.length>1e-6
    if normal.dot(n)<0:ids.reverse();points.reverse();normal=-normal
    normal.normalize();start=len(new_positions)
    for p in points:new_positions.append((p.x,p.z,-p.y));new_normals.append((normal.x,normal.z,-normal.y))
    retained.extend((start+i,) for i in range(3))
   tessellation_report.append({'surface':si,'source_boundary_vertices':len(ring),'removed_triangles':owned[si],'replacement_source_vertex_indices':mapped,'replacement_triangles':len(mapped),'xyz_policy':'exact existing GLB boundary coordinates; normals corrected only for target triangles','projection':'source-local horizontal tangent plus original source height; no XYZ flattening'})
  primitive['attributes']['POSITION']=add_accessor(new_positions);primitive['attributes']['NORMAL']=add_accessor(new_normals);primitive['indices']=add_accessor(retained,'SCALAR',5125)
(DATA/'tessellation_repair.json').write_text(json.dumps({'version':2,'repair_surfaces':[76,81],'preservation_exception':'Only source wall76/81 triangle connectivity and their new outward normals are replaced. All source boundary coordinates, other wall triangles, roof triangles, footing and approved facade overlays remain unchanged.','faces':tessellation_report},indent=2)+'\n')
# Version3: independently evidenced visible wall74 defect, separate bounded repair.
tessellation_report=[]
for mesh in doc['meshes']:
 for primitive in mesh['primitives']:
  if doc['materials'][primitive['material']]['name']!='fukuras_wall':continue
  old_positions=accessor(primitive['attributes']['POSITION']);old_normals=accessor(primitive['attributes']['NORMAL']);old_indices=[v[0] for v in accessor(primitive['indices'])]
  old_world=[Vector((x,-z,y)) for x,y,z in old_positions];retained=[];owned={74:[]};source_rings={si:[Vector(p) for p in D['surfaces'][si]['ring'][:-1]] for si in [74]}
  for ti in range(0,len(old_indices),3):
   ids=old_indices[ti:ti+3];world=[old_world[i] for i in ids];target=None
   for si,ring in source_rings.items():
    if not all(min((p-v).length for v in ring)<.0003 for p in world):continue
    owners=[j for j,surface in enumerate(D['surfaces']) if all(min((p-Vector(v)).length for v in surface['ring'])<.0003 for p in world)]
    assert owners==[si],('Ambiguous source ownership',ti//3,owners)
    assert target is None
    target=si
   if target is None:retained.extend((i,) for i in ids)
   else:owned[target].append({'triangle_index':ti//3,'indices':ids})
  new_positions=list(old_positions);new_normals=list(old_normals)
  for si,ring in source_rings.items():
   assert len(owned[si])==len(ring)-2,(si,len(owned[si]),len(ring))
   o=ring[0];n=Vector((0,0,0))
   for j,p in enumerate(ring):
    q=ring[j-1];n.x+=(p.y-q.y)*(p.z+q.z);n.y+=(p.z-q.z)*(p.x+q.x);n.z+=(p.x-q.x)*(p.y+q.y)
   n.normalize()
   if n.x>0:n=-n
   t=Vector((n.y,-n.x,0))
   uv=[Vector(((p-o).dot(t),p.z,0)) for p in ring]
   triangles=tessellate_polygon([uv]);mapped=[]
   for triangle in triangles:
    ids=list(triangle) if isinstance(triangle[0],int) else [min(range(len(uv)),key=lambda j:(uv[j]-v).length) for v in triangle]
    mapped.append(ids)
   assert len(mapped)==len(ring)-2
   exact=[]
   for point in ring:
    ids=[i for rec in owned[si] for i in rec['indices'] if (old_world[i]-point).length<.0003]
    assert ids;exact.append(old_world[ids[0]].copy())
   for ids in mapped:
    points=[exact[i] for i in ids]
    normal=(points[1]-points[0]).cross(points[2]-points[0])
    assert normal.length>1e-6
    if normal.dot(n)<0:ids.reverse();points.reverse();normal=-normal
    normal.normalize();start=len(new_positions)
    for p in points:new_positions.append((p.x,p.z,-p.y));new_normals.append((normal.x,normal.z,-normal.y))
    retained.extend((start+i,) for i in range(3))
   tessellation_report.append({'surface':si,'source_boundary_vertices':len(ring),'removed_triangles':owned[si],'replacement_source_vertex_indices':mapped,'replacement_triangles':len(mapped),'xyz_policy':'exact existing GLB boundary coordinates; normals corrected only for target triangles','projection':'source-local horizontal tangent plus original source height; no XYZ flattening'})
  primitive['attributes']['POSITION']=add_accessor(new_positions);primitive['attributes']['NORMAL']=add_accessor(new_normals);primitive['indices']=add_accessor(retained,'SCALAR',5125)
(DATA/'tessellation_repair_v2.json').write_text(json.dumps({'version':3,'repair_surfaces':[74],'previous_repair_surfaces':[76,81],'reference_candidate_sha256':'c820b8bb7ef4f833cd4aea474ff9f9fa8566d4f330c6c484be0370f44cef62c8','preservation_exception':'This revision replaces only source wall74 triangle connectivity and its outward normals, retaining the first76/81 correction exactly. All source boundary coordinates, other wall triangles, roof triangles, footing and approved facade overlays remain unchanged.','faces':tessellation_report},indent=2)+'\n')
# Version4: demonstrated source roof35 invalid cap only; no courtyard filling.
tessellation_report=[]
for mesh in doc['meshes']:
 for primitive in mesh['primitives']:
  if doc['materials'][primitive['material']]['name']!='fukuras_roof':continue
  old_positions=accessor(primitive['attributes']['POSITION']);old_normals=accessor(primitive['attributes']['NORMAL']);old_indices=[v[0] for v in accessor(primitive['indices'])]
  old_world=[Vector((x,-z,y)) for x,y,z in old_positions];retained=[];owned={35:[]};source_rings={si:[Vector(p) for p in D['surfaces'][si]['ring'][:-1]] for si in [35]}
  for ti in range(0,len(old_indices),3):
   ids=old_indices[ti:ti+3];world=[old_world[i] for i in ids];target=None
   for si,ring in source_rings.items():
    if not all(min((p-v).length for v in ring)<.0003 for p in world):continue
    owners=[j for j,surface in enumerate(D['surfaces']) if all(min((p-Vector(v)).length for v in surface['ring'])<.0003 for p in world)]
    assert owners==[si],('Ambiguous source ownership',ti//3,owners)
    assert target is None
    target=si
   if target is None:retained.extend((i,) for i in ids)
   else:owned[target].append({'triangle_index':ti//3,'indices':ids})
  new_positions=list(old_positions);new_normals=list(old_normals)
  for si,ring in source_rings.items():
   assert len(owned[si])==len(ring)-2,(si,len(owned[si]),len(ring))
   n=Vector((0,0,1));uv=[Vector((p.x,p.y,0)) for p in ring]
   triangles=tessellate_polygon([uv]);mapped=[]
   for triangle in triangles:
    ids=list(triangle) if isinstance(triangle[0],int) else [min(range(len(uv)),key=lambda j:(uv[j]-v).length) for v in triangle]
    mapped.append(ids)
   assert len(mapped)==len(ring)-2
   exact=[]
   for point in ring:
    ids=[i for rec in owned[si] for i in rec['indices'] if (old_world[i]-point).length<.0003]
    assert ids;exact.append(old_world[ids[0]].copy())
   for ids in mapped:
    points=[exact[i] for i in ids]
    normal=(points[1]-points[0]).cross(points[2]-points[0])
    assert normal.length>1e-6
    if normal.dot(n)<0:ids.reverse();points.reverse();normal=-normal
    normal.normalize();start=len(new_positions)
    for p in points:new_positions.append((p.x,p.z,-p.y));new_normals.append((normal.x,normal.z,-normal.y))
    retained.extend((start+i,) for i in range(3))
   tessellation_report.append({'surface':si,'source_boundary_vertices':len(ring),'removed_triangles':owned[si],'replacement_source_vertex_indices':mapped,'replacement_triangles':len(mapped),'xyz_policy':'exact existing GLB boundary coordinates; normals corrected only for target triangles','projection':'sourceXY projection for the horizontal roof polygon; exact existing boundaryXYZ retained'})
  primitive['attributes']['POSITION']=add_accessor(new_positions);primitive['attributes']['NORMAL']=add_accessor(new_normals);primitive['indices']=add_accessor(retained,'SCALAR',5125)
(DATA/'roof35_repair.json').write_text(json.dumps({'version':4,'repair_surfaces':[35],'previous_wall_repair_surfaces':[74,76,81],'reference_candidate_sha256':'821fb5b27a3e7a4ccbb48cdddc489c030920423c161b4ff250f483342734ab7e','preservation_exception':'This revision replaces only roof source35 connectivity and upward normals, retaining all previous wall repairs and every other roof triangle exactly. All source boundary coordinates, other wall triangles, roof triangles, footing and approved facade overlays remain unchanged.','faces':tessellation_report},indent=2)+'\n')
doc['buffers'][0]['byteLength']=len(binary)
while len(binary)%4:binary.append(0)
j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
(OUT/'fukuras.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary)
repair=json.loads((DATA/'tessellation_repair.json').read_text());repair['scope_note']='Historical76/81 pass; later74 and roof35 passes are recorded separately';repair['preservation_exception']='This file describes earlier76/81 pass only; cumulative repairs also include74 and roof35. All source boundaryXYZ and remaining geometry are unchanged.';repair['current_glb_sha256']=hashlib.sha256((OUT/'fukuras.glb').read_bytes()).hexdigest();(DATA/'tessellation_repair.json').write_text(json.dumps(repair,indent=2)+'\n')
repair74=json.loads((DATA/'tessellation_repair_v2.json').read_text());repair74['scope_note']='Historical wall74 pass; current roof35 repair is separately recorded in roof35_repair.json';repair74['current_glb_sha256']=repair['current_glb_sha256'];(DATA/'tessellation_repair_v2.json').write_text(json.dumps(repair74,indent=2)+'\n')
roofrepair=json.loads((DATA/'roof35_repair.json').read_text());roofrepair['current_glb_sha256']=repair['current_glb_sha256'];(DATA/'roof35_repair.json').write_text(json.dumps(roofrepair,indent=2)+'\n')
stats=json.loads((DATA/'baseline_stats.json').read_text());stats['glb_sha256']=repair['current_glb_sha256'];stats['baseline_glass_panels']=stats['glass_panels'];stats['glass_panels']=sum(doc['accessors'][p['indices']]['count']//6 for m in doc['meshes'] for p in m['primitives'] if doc['materials'][p['material']]['name'].startswith('fukuras_glass'))+sum(v for (si,mat),v in counts.items() if mat=='curtain_glass');stats.update(triangles=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives']),primitives=sum(len(m['primitives']) for m in doc['meshes']),treated_surfaces=mask,removed_overlay_triangles=removed,source_buffers_preserved=True,tessellation_repair_surfaces=[74,76,81],roof_repair_surfaces=[35],this_revision_repair_surfaces=[35],preservation_exception='Roof35 only changes versus wallv2 correction; previous74/76/81 repairs, all boundaryXYZ and off-target geometry retained',ground_sampling='inherited exact baseline; not freshly queried',status='bounded October2025 facade plus source-wall74/76/81 and roof35 bounded tessellation repairs; hidden and upper service facades remain approximation')
(DATA/'stats.json').write_text(json.dumps(stats,indent=2)+'\n');(DATA/'facade_map.json').write_text(json.dumps({'mask':mask,'principal_field_source_z':[42.3,83.9],'pieces':records},indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(OUT/'fukuras.glb'));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/blender/fukuras.blend'))
print(json.dumps({k:v for k,v in stats.items() if k!='pavement_samples'},indent=2))
