"""OSM-positioned small facilities; body type and dimensions are explicit estimates."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src,ground,out,stats=sys.argv[sys.argv.index('--')+1:];D=json.load(open(src));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ground);bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_intersection','ground_sidewalk','ground_fill')):
  me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free()
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
G={};M={};records=[]
for name,color,rough,metal in [('housing',[.42,.44,.42],.7,.4),('roof',[.35,.38,.38],.8,.2),('steel',[.65,.69,.70],.4,.65),('dark',[.012,.014,.015],.9,0),('concrete',[.38,.39,.36],.9,0)]:
 m=bpy.data.materials.new('street_plaza_facilities_'+name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;M[name]=m

def face(name,pts):
 bm=G.setdefault(name,bmesh.new());bm.faces.new([bm.verts.new(p) for p in pts])
def box(c,size,name,angle=0):
 x,y,z=c;w,d,h=size;a,b=math.cos(angle),math.sin(angle);ps=[(x+a*u-b*v,y+b*u+a*v,z+t) for u,v,t in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face(name,[ps[i] for i in ids])
for item in D['items']:
 ring=[Vector((*p,0)) for p in item['ring']];c=sum(ring,Vector())/len(ring);samples=[]
 for p in ring+[c]:
  hit=bvh.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
  samples.append({'xy':[p.x,p.y],'tp':hit.z+15 if hit else None})
 heights=[s['tp']-15 for s in samples if s['tp'] is not None]
 if not heights:raise ValueError('no Core ground: '+item['id'])
 g=min(heights)-.015;h=item['height_m'];edges=[(ring[i-1],p) for i,p in enumerate(ring)]
 if item['kind']=='smoking_cabinet_estimate':
  a,b=max(edges,key=lambda e:(e[1]-e[0]).length);t=(b-a).normalized();n=Vector((-t.y,t.x,0));angle=math.atan2(t.y,t.x);width=(b-a).length;depth=min((p-c).dot(n) for p in ring);depth=max((p-c).dot(n) for p in ring)-depth
  box((c.x,c.y,g+.04),(width,depth,.08),'concrete',angle)
  for k in [-.25,.25]:
   q=c+t*(width*k);w=width*.46
   box((q.x,q.y,g+h*.50),(w,depth*.90,h-.08),'housing',angle)
   box((q.x,q.y,g+h),(w+.02,depth,.055),'steel',angle)
   box((q.x,q.y,g+h+.029),(w*.70,depth*.22,.005),'dark',angle)
   for dz in [.15,.82]:
    r=q+n*(depth*.46);box((r.x,r.y,g+dz),(w*.85,.018,.018),'steel',angle)
 else:
  face('concrete',[(p.x,p.y,g) for p in reversed(ring)]);face('roof',[(p.x,p.y,g+h) for p in ring])
  for a,b in edges:
   face('housing',[(a.x,a.y,g),(b.x,b.y,g),(b.x,b.y,g+h-.12),(a.x,a.y,g+h-.12)])
   face('roof',[(a.x,a.y,g+h-.12),(b.x,b.y,g+h-.12),(b.x,b.y,g+h),(a.x,a.y,g+h)])
   t=(b-a).normalized();n=Vector((-t.y,t.x,0));mid=(a+b)/2
   if n.dot(mid-c)<0:n=-n
   l=(b-a).length;angle=math.atan2(t.y,t.x)
   for k in range(1,math.ceil(l/.9)):
    q=a.lerp(b,k/math.ceil(l/.9))+n*.009;box((q.x,q.y,g+h/2),(.012,.012,h-.2),'steel',angle)
  a,b=max([e for e in edges if (e[1]-e[0]).length>2],key=lambda e:(e[0].y+e[1].y)/2);t=(b-a).normalized();n=Vector((-t.y,t.x,0));p=(a+b)/2
  if n.dot(p-c)<0:n=-n
  p+=n*.035;angle=math.atan2(t.y,t.x)
  box((p.x,p.y,g+1.1),(.95,.045,2.2),'dark',angle)
  box((p.x,p.y,g+1.1),(.88,.065,2.12),'housing',angle)
  q=p+t*.30+n*.04;box((q.x,q.y,g+1.05),(.04,.04,.16),'steel',angle)
  for k in range(8):
   q=p+n*.06;box((q.x,q.y,g+2.50+k*.035),(.65,.035,.015),'dark',angle)
 records.append({'id':item['id'],'kind':item['kind'],'base_tp_m':g+15,'top_tp_m':g+15+h,'ground_samples':samples,'height_estimated_m':h})
counts={}
for name,bm in G.items():
 bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new('street_plaza_facilities_'+name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);counts[name]=len(me.polygons)
Path(out).parent.mkdir(parents=True,exist_ok=True);bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_yup=True)
Path(stats).write_text(json.dumps({'items':records,'triangles':sum(counts.values()),'primitives':len(counts),'datum_tp_m':15,'status':'Standard-shape estimates, not October2025 photo matched. OSM smoking footprint does not establish a complete smoking enclosure.'},indent=1)+'\n');print(records)
