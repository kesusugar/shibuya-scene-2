"""Portable PARCO northeast podium refinement. Blender 4.2.3, no external Python modules.
Run: blender -b --python-exit-code 1 -t 4 -P source/blender/build_podium.py
Paths derive from this script; only seven proven source108/152 index triangles and two target152 normals change.
"""
from pathlib import Path
import bpy, json, math, struct, hashlib, sys
from mathutils import Vector, Quaternion
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'source/data'; WEB=ROOT/'web'
for inp in json.loads((DATA/'required_inputs.json').read_text())['inputs']:
    raw=(ROOT/inp['path']).read_bytes()
    assert len(raw)==inp['bytes'] and hashlib.sha256(raw).hexdigest()==inp['sha256'],f"Input hash mismatch: {inp['path']}"
LAYOUT=json.loads((DATA/'podium_layout.json').read_text())
assert bpy.app.version[:3]==(4,2,3), f'Requires Blender4.2.3, got {bpy.app.version_string}'
baseline=ROOT/'source/inputs/baseline.glb'
assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='9fa2046b02ac220b305c67241a19b607ea39d2e0a7beedd953cb0a761d3152e2'
assert hashlib.sha256((DATA/'plateau.json').read_bytes()).hexdigest()=='031a66d351a04474ffef5346264e1871f50f6d292bdd898d20bce7ca6bb644a1'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from repair_podium_topology import repair_podium_topology
patched_bytes,repair_report=repair_podium_topology(baseline.read_bytes())
patched_baseline=DATA/'baseline_podium_topology_corrected.glb';patched_baseline.write_bytes(patched_bytes)
(DATA/'topology_repair.json').write_text(json.dumps(repair_report,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(patched_baseline))
originals=list(bpy.context.scene.objects)
for o in originals: o['original_positions_preserved']=True

def material(name,color,roughness=.6,metallic=0,alpha=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=roughness;bs.inputs['Alpha'].default_value=alpha
    if alpha<1:m.surface_render_method='DITHERED';m.use_transparency_overlap=False
    return m
mats={
'cladding':material('parco_podium_cladding',(.67,.675,.65),.78),
'joint':material('parco_podium_joint',(.24,.27,.27),.58,.15),
'glass':material('parco_podium_glass',(.15,.245,.255),.24,.28),
'rail_glass':material('parco_podium_rail_glass',(.35,.52,.55),.18,.15,.32)}
V={k:[] for k in mats};F={k:[] for k in mats};component_log=[]

def prism(k,zone,u0,u1,z0,z1,d0,d1,kind):
    # Full small rectangular prism. Facade normal is right of directed horizontal tangent.
    a=Vector((*zone['a'],0));b=Vector((*zone['b'],0));t=(b-a).normalized();n=Vector((t.y,-t.x,0)); base=len(V[k])
    for u,z,d in [(u0,z0,d0),(u1,z0,d0),(u1,z1,d0),(u0,z1,d0),(u0,z0,d1),(u1,z0,d1),(u1,z1,d1),(u0,z1,d1)]:
        V[k].append(tuple(a+t*u+n*d+Vector((0,0,z))))
    for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)]:F[k].append(tuple(base+i for i in f))
    component_log.append(dict(face=zone['face'],kind=kind,material=k,u=[u0,u1],z=[z0,z1],depth=[d0,d1]))

p=LAYOUT['parameters']
for zone in LAYOUT['zones']:
    L=(Vector(zone['b'])-Vector(zone['a'])).length
    z0=zone['z_min']; pb=zone['panel_bottom'];top=zone['z_max']-.035
    # Backing makes joints a real narrow reveal. Large 2.5m x 4m panels are not window bays.
    prism('joint',zone,.005,L-.005,pb,top,.045,.30,'reveal_backing')
    w=L/zone['panel_cols'];h=(top-pb)/zone['panel_rows'];j=p['joint_width']
    for c in range(zone['panel_cols']):
      for r in range(zone['panel_rows']):
        prism('cladding',zone,c*w+j/2,(c+1)*w-j/2,pb+r*h+j/2,pb+(r+1)*h-j/2,.30,.48,'pale_cladding_panel')
    # The source solid remains behind this shallow facade layer; no artificial multi-metre recess.
    prism('joint',zone,.01,L-.01,z0+.02,pb,.03,.045,'shadow_backing')
    bays=max(1,round(L/p['glass_bay_width_approx'])); bw=L/bays
    floor=z0+.08; ceiling=pb-.28
    for c in range(bays):
      for r in range(2):
        za=floor+(ceiling-floor)*r/2;zb=floor+(ceiling-floor)*(r+1)/2
        prism('glass',zone,c*bw+.04,(c+1)*bw-.04,za+.04,zb-.04,.045,.065,'terrace_glazing')
    for i in range(bays+1):
        u=min(L-.04,max(.04,i*bw));prism('joint',zone,u-.032,u+.032,floor,ceiling,.065,.105,'slim_glass_mullion')
    for z in [floor,(floor+ceiling)/2,ceiling]:
        prism('joint',zone,.01,L-.01,z-.03,z+.03,.065,.105,'slim_glass_transom')
    # Thin overhang/fascia and pale slender structural piers give three-dimensional hierarchy.
    prism('cladding',zone,.015,L-.015,pb-.22,pb,.05,.48,'shallow_soffit_edge')
    for frac in zone['support_u_fractions']:
        u=frac*L;prism('cladding',zone,u-.29,u+.29,z0+.04,pb,.10,.52,'pale_support')
    prism('cladding',zone,.015,L-.015,z0,z0+.12,.04,.53,'terrace_edge')
    railz=z0+.12
    rbays=max(1,round(L/1.6));rw=L/rbays
    for c in range(rbays):
        prism('rail_glass',zone,c*rw+.024,(c+1)*rw-.024,railz+.045,railz+1.10,.50,.518,'glass_balustrade')
    for i in range(rbays+1):
        u=min(L-.03,max(.03,i*rw));prism('joint',zone,u-.018,u+.018,railz,railz+1.12,.515,.55,'rail_post')
    prism('joint',zone,.01,L-.01,railz+1.10,railz+1.12,.515,.55,'rail_top')

added=[]
for k in mats:
    mesh=bpy.data.meshes.new('parco_podium_'+k);mesh.from_pydata(V[k],[],F[k]);mesh.materials.append(mats[k]);mesh.update()
    obj=bpy.data.objects.new('parco_podium_'+k,mesh);bpy.context.collection.objects.link(obj);added.append(obj)
    obj['source_faces']='171, upper108, eastern152';obj['inferred_shallow_relief']=True;obj['max_depth_m']=.55

# Export only additional meshes, then concatenate glTF binary buffers without touching old data.
bpy.ops.object.select_all(action='DESELECT')
for o in added:o.select_set(True)
bpy.context.view_layer.objects.active=added[0]
tmp=DATA/'podium_additions.glb'
bpy.ops.export_scene.gltf(filepath=str(tmp),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
def readglb(path):
    raw=path.read_bytes();jlen=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jlen]);bpos=20+jlen;blen=struct.unpack_from('<I',raw,bpos)[0];return doc,raw[bpos+8:bpos+8+blen]
a,ab=readglb(patched_baseline);b,bb=readglb(tmp)
# Baseline JSON, all XYZ, all materials and non-target attributes stay unchanged. Only seven audited108/152 index triplets and two target152 normals differ.
off={k:len(a.get(k,[])) for k in ['bufferViews','accessors','meshes','materials','nodes']};align=(-len(ab))%4;boff=len(ab)+align
for v in b.get('bufferViews',[]):v['buffer']=0;v['byteOffset']=v.get('byteOffset',0)+boff
for ac in b.get('accessors',[]):
    if 'bufferView' in ac:ac['bufferView']+=off['bufferViews']
for me in b.get('meshes',[]):
  for pr in me['primitives']:
    pr['attributes']={k:v+off['accessors'] for k,v in pr['attributes'].items()}
    if 'indices' in pr:pr['indices']+=off['accessors']
    if 'material' in pr:pr['material']+=off['materials']
for node in b.get('nodes',[]):
    if 'mesh' in node:node['mesh']+=off['meshes']
    if 'children' in node:node['children']=[v+off['nodes'] for v in node['children']]
for k in off:a.setdefault(k,[]).extend(b.get(k,[]))
a['scenes'][a.get('scene',0)].setdefault('nodes',[]).extend(v+off['nodes'] for v in b['scenes'][b.get('scene',0)].get('nodes',[]))
for extkey in ['extensionsUsed','extensionsRequired']:
    if extkey in b:a[extkey]=sorted(set(a.get(extkey,[])+b[extkey]))
newbin=ab+b'\0'*align+bb;a['buffers']=[{'byteLength':len(newbin)}]
a['asset']['generator']='PARCO additive podium pass; Blender4.2.3; baseline attributes retained; source108/152 bounded topology repair'
jraw=json.dumps(a,separators=(',',':')).encode();jraw+=b' '*((-len(jraw))%4);newbin+=b'\0'*((-len(newbin))%4)
raw=struct.pack('<III',0x46546c67,2,12+8+len(jraw)+8+len(newbin))+struct.pack('<II',len(jraw),0x4e4f534a)+jraw+struct.pack('<II',len(newbin),0x004e4942)+newbin
WEB.mkdir(exist_ok=True);(WEB/'parco.glb').write_bytes(raw)
tmp.unlink();patched_baseline.unlink()
# Packed, redistributable CC0 reference. Non-rendering and excluded from exported GLB.
ref=bpy.data.images.load(str(ROOT/'source/refs/MAR04-2024-full.jpg'));ref.name='Reference_Syced_2024-03-04_CC0_auxiliary_not_2025';ref.pack();ref.filepath='//refs/MAR04-2024-full.jpg'
ref_obj=bpy.data.objects.new('REFERENCE_CC0_2024_auxiliary_only',None);bpy.context.collection.objects.link(ref_obj);ref_obj.empty_display_type='IMAGE';ref_obj.data=ref;ref_obj.empty_display_size=30;ref_obj.location=(-200,320,30);ref_obj.rotation_euler=(math.pi/2,0,0);ref_obj.hide_render=True
ref['source_url']='https://commons.wikimedia.org/wiki/File:Shibuya_Parco.jpg';ref['license']='CC0 1.0';ref['temporal_limit']='Auxiliary permanent architecture only; not 2025 proof'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='PROPERTIES':
            area.type='IMAGE_EDITOR'
            for space in area.spaces:
                if space.type=='IMAGE_EDITOR':space.image=ref
        elif area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=Vector((-130,295,39));area.spaces.active.region_3d.view_distance=90
            area.spaces.active.region_3d.view_rotation=Quaternion((.834,.473,.139,.247));area.spaces.active.shading.type='MATERIAL'
# Neutral photographic-angle review setup; environment and camera are not exported.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Review_sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.74,.82,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN',location=(-80,350,140));sun=bpy.context.object;sun.name='Review_sun';sun.rotation_euler=Vector((-.65,-.55,-1)).to_track_quat('-Z','Y').to_euler();sun.data.energy=2.2;sun.data.angle=.12
bpy.ops.object.camera_add(location=(-74,354,10.1));cam=bpy.context.object;cam.name='Review_NE_photo_angle';cam.rotation_euler=(Vector((-126,296,37))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=50;s.camera=cam
bpy.ops.object.select_all(action='DESELECT')
for o in added:o.select_set(True)
bpy.context.view_layer.objects.active=added[0]
text=bpy.data.texts.new('READ_ME_REFERENCE_AND_LIMITS');text.write('PARCO north-east podium: SHALLOW RELIEF PROTOTYPE. Original source coordinates and roof unchanged. Seven invalid source108/152 triangle index triples and two exclusively targeted152 normals corrected. CC0 image packed in Image Editor, date2024-03-04, auxiliary only. October2025 caption-dated photo is reference-only, not embedded. No deep terrace excavation. Exact divisions/depths inferred. See README.md and source/data/podium_layout.json.\n')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/parco_podium.blend'))
prims=[p for m in a['meshes'] for p in m['primitives']];tri=sum(a['accessors'][q['indices']]['count']//3 for q in prims)
stats={'triangles':tri,'primitives':len(prims),'bytes':len(raw),'roof_translation_m':0,'glass_panels':sum(x['kind']=='terrace_glazing' for x in component_log),'glass_panels_scope':'added terrace glazing only; inherited office panes not recounted','podium_added_triangles':sum(len(F[k])*2 for k in mats),'podium_added_primitives':4,'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(raw).hexdigest(),'original_positions_retained_verbatim':True,'source108_index_repair_triangle_count':2,'source152_index_repair_triangle_count':5,'source152_normal_vertices_repaired':2,'non_target_triangles_retained_verbatim':True,'components':component_log}
(DATA/'stats.json').write_text(json.dumps(stats,indent=2)+'\n')
print('PARCO_STATS',json.dumps({k:v for k,v in stats.items() if k!='components'}))
