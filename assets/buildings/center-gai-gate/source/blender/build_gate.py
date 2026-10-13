"""Photo-type entrance arch, Blender 4.2.3; no campaign artwork.
blender -b -P build_gate.py -- layout.json ground.glb outdir
All output coordinates use T.P.-15; groundElevationTP=15 in viewer hints.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

layout, ground, output = sys.argv[sys.argv.index('--')+1:][:3]
assert bpy.app.version == (4,2,3)
L=json.loads(Path(layout).read_text());OUT=Path(output);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ground)
bm=bmesh.new()
for ob in list(bpy.context.scene.objects):
    if ob.type=='MESH' and ob.name.startswith(('ground_road','ground_intersection','ground_sidewalk','ground_fill')):
        me=ob.data.copy();me.transform(ob.matrix_world);bm.from_mesh(me);bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm);bm.free();feet=[]
for i,(x,y) in enumerate(L['foot_points']):
    hits=[]
    for dx,dy in [(0,0),(-.22,0),(.22,0),(0,-.22),(0,.22)]:
        hit=bvh.ray_cast(Vector((x+dx,y+dy,80)),Vector((0,0,-1)))[0]
        if hit:hits.append({'x':x+dx,'y':y+dy,'tp':hit.z+15})
    assert len(hits)>=3, f'Foot {i}: insufficient ground coverage'
    tp=sorted(h['tp'] for h in hits)[len(hits)//2]
    feet.append({'xy':[x,y],'tp':tp,'min_tp':min(h['tp'] for h in hits),'max_tp':max(h['tp'] for h in hits),'samples':hits})
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
A,B=[Vector((*f['xy'],f['tp']-15)) for f in feet];span=(Vector(B.xy)-Vector(A.xy)).length
T=Vector((B.x-A.x,B.y-A.y,0)).normalized();N=Vector((T.y,-T.x,0));Z=Vector((0,0,1))
M={};G={}
def mat(name,rgb,metal=0,rough=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[name]=m
mat('gate_frame',(.025,.03,.026),.45,.38);mat('gate_panel',tuple(L['panel_color']),0,.64)
mat('gate_base',(.30,.31,.28),0,.83);mat('gate_lamp',(.68,.70,.62),.1,.4)
def face(name,pts):
    bm=G.setdefault(name,bmesh.new());f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
def tube(name,path,radius,sides=16):
    rings=[]
    for i,p in enumerate(path):
        tangent=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized()
        v=tangent.cross(N).normalized()
        rings.append([p+N*(radius*math.cos(2*math.pi*j/sides))+v*(radius*math.sin(2*math.pi*j/sides)) for j in range(sides)])
    for a,b in zip(rings,rings[1:]):
        for j in range(sides):face(name,[a[j],a[(j+1)%sides],b[(j+1)%sides],b[j]])
    face(name,list(reversed(rings[0])));face(name,rings[-1])
def arch(u):
    # Cubic with vertical shoulder tangents and a smooth horizontal top.
    p0=A+Z*L['shoulder_height_m'];p3=B+Z*L['shoulder_height_m']
    lift=L['arch_rise_m']*4/3
    p1=p0+Z*lift;p2=p3+Z*lift
    return p0*(1-u)**3+p1*(3*(1-u)**2*u)+p2*(3*(1-u)*u*u)+p3*u**3

for i,p in enumerate([A,B]):
    bottom=feet[i]['min_tp']-15-.025
    tube('gate_base',[Vector((p.x,p.y,bottom)),p+Z*L['base_height_m']],L['base_radius_m'])
    tube('gate_frame',[p+Z*L['base_height_m'],p+Z*L['shoulder_height_m']],L['post_radius_m'])
path=[arch(i/L['arch_steps']) for i in range(L['arch_steps']+1)]
tube('gate_frame',path,L['arch_radius_m'])
start=(1-L['panel_width_fraction'])/2;end=1-start
segments=32
front=[];back=[]
for i in range(segments+1):
    u=start+(end-start)*i/segments;top=arch(u)-Z*.14;bottom=top-Z*L['panel_height_m']
    front.append((top+N*L['panel_depth_m']/2,bottom+N*L['panel_depth_m']/2))
    back.append((top-N*L['panel_depth_m']/2,bottom-N*L['panel_depth_m']/2))
for i in range(segments):
    a,b=front[i],front[i+1];c,d=back[i],back[i+1]
    face('gate_panel',[a[1],b[1],b[0],a[0]]);face('gate_panel',[c[0],d[0],d[1],c[1]])
    face('gate_frame',[a[0],b[0],d[0],c[0]]);face('gate_frame',[c[1],d[1],b[1],a[1]])
for i in [0,segments]:face('gate_frame',[front[i][0],front[i][1],back[i][1],back[i][0]])
for u in (.25,.5,.75):
    p=arch(u)-Z*(L['panel_height_m']+.24)+N*.12
    tube('gate_frame',[p+Z*.10,p-Z*.05],.11)
    tube('gate_lamp',[p-Z*.055,p-Z*.075],.085)

counts={}
for name,bm in G.items():
    bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]=len(me.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(OUT/'center-gai-gate.glb'),export_format='GLB',export_yup=True)
hints={'groundElevationTP':15,'planBounds':[min(A.x,B.x)-.4,min(A.y,B.y)-.4,max(A.x,B.x)+.4,max(A.y,B.y)+.4],'sun':{'azimuth_deg':207,'elevation_deg':57}}
(OUT/'viewer.json').write_text(json.dumps(hints,indent=2)+'\n')
for mode in ['day','night']:
    emit={'gate_lamp':{'kind':'interior','emit':[1,.95,.78],'estr':L['night_emission'] if mode=='night' else L['day_emission']}}
    (OUT/f'emissive_{mode}.json').write_text(json.dumps(emit,indent=2)+'\n')
stats={'id':L['id'],'source_id':L['source_id'],'datum_tp_m':15,'feet':feet,'span_m':span,'top_local_m':max(p.z for p in path)+L['arch_radius_m'],'min_clear_height_m':min(p[1].z for p in front)-max(A.z,B.z),'triangles':sum(counts.values()),'primitives':len(counts),'materials':counts,'position_basis':L['position_basis'],'status':'B photo-type prototype; foot placement and dimensions estimated, no ad content'}
Path(layout).with_name('stats.json').write_text(json.dumps(stats,indent=2)+'\n')
print('GATE',stats['triangles'],stats['primitives'],[f['tp'] for f in feet],stats['min_clear_height_m'])
