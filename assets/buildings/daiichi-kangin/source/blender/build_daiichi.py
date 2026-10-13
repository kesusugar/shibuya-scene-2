"""PLATEAU shell and photo-type facade of Daiichi Kangin, Blender 4.2.3.
blender -b -P build_daiichi.py -- plateau.json layout.json ground.glb webdir
Input and output use common T.P.15 m; only the base skirt follows measured pavement.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, layout, ground, output = sys.argv[sys.argv.index('--')+1:][:4]
assert bpy.app.version == (4, 2, 3)
D = json.loads(Path(source).read_text()); L = json.loads(Path(layout).read_text())
OUT = Path(output); OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ground)
bm = bmesh.new()
for ob in list(bpy.context.scene.objects):
    if ob.type == 'MESH' and ob.name.startswith(('ground_road', 'ground_intersection', 'ground_sidewalk', 'ground_fill')):
        me = ob.data.copy(); me.transform(ob.matrix_world); bm.from_mesh(me); bpy.data.meshes.remove(me)
bvh = BVHTree.FromBMesh(bm); bm.free()
samples = []
for fac in L['facades']:
    a, b, n = Vector(fac['a']), Vector(fac['b']), Vector(fac['normal'])
    for i in range(31):
        p = a.lerp(b, i/30) + n*.35
        hit = bvh.ray_cast(Vector((p.x,p.y,80)), Vector((0,0,-1)))[0]
        if hit: samples.append({'facade':fac['name'],'u':i/30,'x':p.x,'y':p.y,'tp':hit.z+15})
assert samples, 'No measured frontage pavement'
for ob in list(bpy.context.scene.objects): bpy.data.objects.remove(ob, do_unlink=True)

M = {}; GROUP = {}
def mat(name, rgb, metal=0, rough=.65):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    M[name]=m
for name, col, metal, rough in [
    ('dk_wall',(.59,.58,.53),0,.75), ('dk_roof',(.28,.29,.27),0,.9),
    ('dk_frame',(.65,.66,.63),.5,.4), ('dk_glass',tuple(L.get('glass_color',[.10,.17,.18])),.25,.28),
    ('dk_shop_glass',(.025,.045,.044),.15,.36), ('dk_infill',(.46,.035,.028),0,.65),
    ('dk_sign_back',(.034,.041,.04),.2,.7), ('dk_sign_trim',(.66,.52,.25),.45,.42),
    ('dk_shop_light',(.72,.63,.42),0,.55), ('dk_panel_joint',(.30,.31,.29),0,.7)]:
    mat(name,col,metal,rough)

def face(name, pts):
    bm=GROUP.setdefault(name,bmesh.new())
    clean=[]
    for p in pts:
        p=Vector(p)
        if not clean or (p-clean[-1]).length>1e-6: clean.append(p)
    if len(clean)>1 and (clean[0]-clean[-1]).length<1e-6:clean.pop()
    if len(clean)>=3:
        f=bm.faces.new([bm.verts.new(p) for p in clean]); f.normal_update()

# Retain every source surface, including roof and upper advertising mass. No common window texture.
for s in D['surfaces']:
    face('dk_wall' if s['kind']=='WallSurface' else 'dk_roof',s['ring'])
BASE = D['ground_tp']-15
def panel(fac, u, z, w, h, material, offset=.09):
    a,b=Vector((*fac['a'],0)),Vector((*fac['b'],0));t=(b-a).normalized();n=Vector((*fac['normal'],0))
    c=a.lerp(b,u)+n*offset+Vector((0,0,BASE+z))
    face(material,[c-t*w/2-Vector((0,0,h/2)),c+t*w/2-Vector((0,0,h/2)),c+t*w/2+Vector((0,0,h/2)),c-t*w/2+Vector((0,0,h/2))])

for fac in L['facades']:
    length=fac['length_m']; bays=fac['bay_count']; pitch=length/bays
    for floor,z in enumerate(fac['levels_m']):
        for bay in range(bays):
            u=(bay+.5)/bays
            # Large east screen occupies upper glazing, instead of creating windows across it.
            display=fac['name']=='east' and .035<u<.56 and z>20
            if display:continue
            panel(fac,u,z,pitch-.20,L['window_height_m'],'dk_glass')
            if fac['name']=='south' and bay in (1,4,7) and floor<5:
                panel(fac,u,z-1.05,pitch-.23,.55,'dk_infill',.13)
        panel(fac,.5,z-L['window_height_m']/2-.13,length,.18,'dk_frame',.15)
    for bay in range(bays+1):
        panel(fac,bay/bays,16.6,L['mullion_width_m'],30.8,'dk_frame',.16)
    # Recessed ground-floor entrances and broad shop-front sign housings. Tenant content deferred.
    for u in (.16,.48,.80):
        panel(fac,u,1.5,length*.26,2.8,'dk_shop_glass',.13)
        panel(fac,u,3.25,length*.28,.75,'dk_sign_back',.19)
        panel(fac,u,2.9,length*.25,.08,'dk_shop_light',.22)
    for z in (6.3,10.1,13.9,17.7):
        panel(fac,.5,z,length-.3,1.05,'dk_sign_back',.20)
        panel(fac,.5,z-.59,length,.10,'dk_sign_trim',.24)
    # Close the surveyed ground gap only with a skirt; never shift the source roof.
    a,b,n=Vector((*fac['a'],0)),Vector((*fac['b'],0)),Vector((*fac['normal'],0))
    hits=[s for s in samples if s['facade']==fac['name']]
    for i in range(30):
        u0,u1=i/30,(i+1)/30;p0=a.lerp(b,u0)+n*.025;p1=a.lerp(b,u1)+n*.025
        z0=min(hits,key=lambda s:abs(s['u']-u0))['tp']-15
        z1=min(hits,key=lambda s:abs(s['u']-u1))['tp']-15
        face('dk_wall',[(p0.x,p0.y,BASE+.05),(p1.x,p1.y,BASE+.05),(p1.x,p1.y,z1-.03),(p0.x,p0.y,z0-.03)])

east=L['facades'][1];s=L['east_display']
panel(east,s['center_u'],s['center_z'],s['width_m'],s['height_m'],'dk_sign_back',.25)
for z in (s['center_z']-s['height_m']/2,s['center_z']+s['height_m']/2):
    panel(east,s['center_u'],z,s['width_m']+.15,.12,'dk_frame',.29)
for u in [s['center_u']-s['width_m']/east['length_m']/2,s['center_u']+s['width_m']/east['length_m']/2]:
    panel(east,u,s['center_z'],.12,s['height_m'],'dk_frame',.29)
# Source rooftop billboard tower remains plain; only architectural panel joints are added.
south=L['facades'][0]
for z in (34.5,38.5,42.5,46.5,50.5): panel(south,.12,z,4.85,.045,'dk_panel_joint',.04)

counts={}; roof=[]
for name,bm in GROUP.items():
    bmesh.ops.triangulate(bm,faces=bm.faces[:]);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    me.materials.append(M[name]);me.calc_loop_triangles();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    counts[name]=len(me.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(OUT/'daiichi-kangin.glb'),export_format='GLB',export_yup=True)
pts=[p for s in D['surfaces'] for p in s['ring']]
hints={'groundElevationTP':15,'planBounds':[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],'sun':{'azimuth_deg':207,'elevation_deg':57}}
(OUT/'viewer.json').write_text(json.dumps(hints,indent=2)+'\n')
for mode in ['day','night']:
    emit={'dk_shop_glass':{'kind':'interior','emit':[1,.84,.62],'estr':.35 if mode=='night' else 0},'dk_shop_light':{'kind':'interior','emit':[1,.84,.62],'estr':.7 if mode=='night' else 0}}
    (OUT/f'emissive_{mode}.json').write_text(json.dumps(emit,indent=2)+'\n')
stats={'source_id':D['id'],'plateau_id':D['plateau_id'],'datum_tp_m':15,'source_ground_tp':D['ground_tp'],'roof_deviation_m':0,'pavement_samples':samples,'pavement_min_tp':min(s['tp'] for s in samples),'pavement_max_tp':max(s['tp'] for s in samples),'triangles':sum(counts.values()),'primitives':len(counts),'materials':counts,'status':L['status']}
Path(layout).with_name('stats.json').write_text(json.dumps(stats,indent=2)+'\n')
print('DAIICHI',stats['triangles'],stats['primitives'],len(samples),stats['pavement_min_tp'],stats['pavement_max_tp'])
