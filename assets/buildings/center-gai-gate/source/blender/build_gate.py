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
# Claude review R2: WB01 (2025-01, CC0) and the 2025-02 high view show two separate light-grey crook posts whose tops
# bend in towards the street centre, with a flat banner hung between the tips - not one continuous dark arch with a
# curved yellow panel. Dimensions remain estimates (photo proportions: banner ~4.3 x crook height / 1.3 m tall).
mat('gate_crook',tuple(L.get('crook_color',[.78,.79,.78])),.35,.4)
def crook(p,toward):
    """Vertical post, then a quarter bend of radius R toward the centre, ending in a short drooping tip."""
    H=L['crook_bend_height_m'];R=L['crook_radius_m'];pts=[p+Z*L['base_height_m'],p+Z*H]
    c=p+Z*H+toward*R
    for k in range(1,17):
        a=math.pi/2*k/16;pts.append(c-toward*R*math.cos(a)+Z*R*math.sin(a))
    tip=pts[-1]
    for k in range(1,9):
        a=math.pi/2*k/8;pts.append(tip+toward*.45*math.sin(a)-Z*.45*(1-math.cos(a)))
    return pts
tips=[]
for i,(p,toward) in enumerate([(A,T),(B,-T)]):
    bottom=feet[i]['min_tp']-15-.025
    tube('gate_base',[Vector((p.x,p.y,bottom)),p+Z*L['base_height_m']],L['base_radius_m'])
    path=crook(p,toward)
    tube('gate_crook',path[:2],L['post_radius_m'])
    tube('gate_crook',path[1:],L['crook_tube_radius_m'],20)
    # collar ring where the post meets the thicker crook (visible joint in WB01)
    tube('gate_frame',[path[1]-Z*.12,path[1]+Z*.08],L['crook_tube_radius_m']+.04,20)
    tips.append(path[-1])
    tube('gate_lamp',[path[-1]-Z*.02,path[-1]-Z*.16],.11,16)
# Flat banner between the tips: structural backing (gate_panel, dark) plus the January-2025 banner in a separate layer.
la,lb=tips;mid_top=(la+lb)/2-Z*.25;W=L['banner_width_m'];Hb=L['banner_height_m']
c=mid_top-Z*Hb/2;tl=c-T*W/2+Z*Hb/2;tr=c+T*W/2+Z*Hb/2;br=c+T*W/2-Z*Hb/2;bl=c-T*W/2-Z*Hb/2
d=N*L['panel_depth_m']/2
face('gate_panel',[bl-d,br-d,tr-d,tl-d]);face('gate_panel',[tl+d,tr+d,br+d,bl+d])
for a,b in [(tl,tr),(bl,br)]:face('gate_frame',[a-d,b-d,b+d,a+d])
for a,b in [(tl,bl),(tr,br)]:face('gate_frame',[a-d,b-d,b+d,a+d])
# hangers from the crook tips to the banner corners
for tip,corner in [(la,tl),(lb,tr)]:tube('gate_frame',[tip,corner],.02,8)
SIGN=bmesh.new();uv=SIGN.loops.layers.uv.verify()
for off,quad,uvs in [(d+N*.01,[bl,br,tr,tl],[(0,0),(1,0),(1,1),(0,1)]),(-d-N*.01,[br,bl,tl,tr],[(0,0),(1,0),(1,1),(0,1)])]:
    f=SIGN.faces.new([SIGN.verts.new(q+off) for q in quad])
    for l,q in zip(f.loops,uvs):l[uv].uv=q
sm=bpy.data.materials.new('gate_sign_banner');sm.use_nodes=True;bp=sm.node_tree.nodes['Principled BSDF']
tx=sm.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(Path(layout).parent.parent/'textures'/L['banner_texture']))
sm.node_tree.links.new(tx.outputs['Color'],bp.inputs['Base Color']);sm.node_tree.links.new(tx.outputs['Color'],bp.inputs['Emission Color']);bp.inputs['Emission Strength'].default_value=1;bp.inputs['Roughness'].default_value=.8
path=tips
front=[(tl,bl)]
counts={}
for name,bm in G.items():
    bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(M[name]);me.calc_loop_triangles()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);counts[name]=len(me.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(OUT/'center-gai-gate.glb'),export_format='GLB',export_yup=True)
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
me=bpy.data.meshes.new('gate_sign_banner');SIGN.to_mesh(me);SIGN.free();me.materials.append(sm)
ob=bpy.data.objects.new('gate_sign_banner',me);bpy.context.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=str(OUT/'signs-2025-01.glb'),export_format='GLB',export_yup=True)
hints={'groundElevationTP':15,'layers':{'signs':'signs-2025-01.glb'},'planBounds':[min(A.x,B.x)-.4,min(A.y,B.y)-.4,max(A.x,B.x)+.4,max(A.y,B.y)+.4],'sun':{'azimuth_deg':207,'elevation_deg':57}}
(OUT/'viewer.json').write_text(json.dumps(hints,indent=2)+'\n')
for mode in ['day','night']:
    emit={'gate_lamp':{'kind':'interior','emit':[1,.95,.78],'estr':L['night_emission'] if mode=='night' else L['day_emission']},'gate_sign_banner':{'kind':'led','emit':[1,.92,.8],'estr':.5 if mode=='night' else 0}}
    (OUT/f'emissive_{mode}.json').write_text(json.dumps(emit,indent=2)+'\n')
stats={'id':L['id'],'source_id':L['source_id'],'datum_tp_m':15,'feet':feet,'span_m':span,'top_local_m':max(p.z for p in path)+L['crook_tube_radius_m'],'min_clear_height_m':bl.z-max(A.z,B.z),'triangles':sum(counts.values()),'primitives':len(counts),'materials':counts,'position_basis':L['position_basis'],'status':'B photo-type prototype; two crook posts and a flat banner (Claude review R2); foot placement and dimensions estimated; banner = January 2025 photo extract in the signs layer'}
Path(layout).with_name('stats.json').write_text(json.dumps(stats,indent=2)+'\n')
print('GATE',stats['triangles'],stats['primitives'],[f['tp'] for f in feet],stats['min_clear_height_m'])
