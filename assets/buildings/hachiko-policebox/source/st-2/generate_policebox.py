#!/usr/bin/env python3
"""Standalone facade study. Run only with the pinned Blender 4.2.3 executable.
No photo textures, external files, placement, station geometry, or runtime changes.
"""
import argparse, hashlib, json, math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', default=str(ROOT))
parser.add_argument('--no-render', action='store_true')
parser.add_argument('--skip-top-render', action='store_true', help='Keep existing unaffected top silhouette when refreshing lower-support views.')
args = parser.parse_args(argv)
OUT = Path(args.output_dir).resolve(); OUT.mkdir(parents=True, exist_ok=True)
PARAMS = json.loads((ROOT / 'estimated_dimensions.json').read_text())
P = {k: v['value'] for k, v in PARAMS['parameters'].items()}
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
base = bpy.data.collections.get('Collection')
if base: bpy.data.collections.remove(base)
COL = {}
for name in ['SOURCE_VISIBLE_20250409','ESTIMATED_CLOSURE','REVIEW_ONLY']:
    COL[name] = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(COL[name])
SRC='SOURCE_VISIBLE_20250409'; EST='ESTIMATED_CLOSURE'; REVIEW='REVIEW_ONLY'
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
scene['asset_status']=PARAMS['status']; scene['reference_date']=PARAMS['reference_date']; scene['metric_scale_is_estimated']=True
scene['origin_description']=PARAMS['origin']; scene['source_photos_included']=False

def mat(name, color, metal=0, rough=.45, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=emission
    return m
silver=mat('Silver satin exterior | estimated',(.58,.62,.62),.72,.31)
silver_edge=mat('Silver edge | estimated',(.42,.47,.47),.72,.34)
green=mat('Pale green lined surface | material unconfirmed',(.47,.64,.59),.20,.38)
green_line=mat('Fine green lining | geometric proxy',(.36,.49,.46),.18,.50)
dark=mat('Shallow dark opening | no interior',(.035,.055,.06),.15,.33)
window=mat('Upper visible aperture pane proxy',(.09,.14,.145),.22,.30)
red=mat('Visible red support strip',(.40,.028,.043),.18,.38)
stone=mat('Provisional lower threshold',(.27,.25,.22),0,.80)
white=mat('Plain sign face',(.75,.78,.76),.20,.45)
letters=mat('Plain KOBAN lettering | not exact sign artwork',(.29,.36,.45),.15,.45)
seam=mat('Soft panel seam',(.29,.33,.32),.45,.48)
cyan=mat('CONFIDENCE: source-visible component, dimensions estimated',(.08,.55,.62),.1,.5)
orange=mat('CONFIDENCE: estimated closure and hidden continuation',(.98,.32,.06),.05,.5)
labelmat=mat('Review label',(.11,.16,.19),0,.7,1)


def link(obj, collection, material=None):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    COL[collection].objects.link(obj)
    if material: obj.data.materials.append(material)
    obj['component_scope']=collection; obj['estimated_dimensions']=True
    obj['reference_date']='2025-04-09'; obj['not_georeferenced']=True
    return obj

def box(name, loc, scale, material=silver, collection=SRC, bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link(o,collection,material)
    if bevel:
        m=o.modifiers.new('Small manufactured edge, estimated','BEVEL'); m.width=min(bevel,min(scale)*0.22); m.segments=2
        m.affect='EDGES'
        n=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL'); n.keep_sharp=True; n.weight=30
    return o

def mesh(name, verts, faces, material, collection=SRC):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); COL[collection].objects.link(o); me.materials.append(material)
    o['component_scope']=collection; o['estimated_dimensions']=True; o['reference_date']='2025-04-09'
    return o

def cylinder(name,x,y,z0,z1,r,material=silver,collection=SRC):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=z1-z0, end_fill_type='NGON',location=(x,y,(z0+z1)/2))
    o=bpy.context.object;o.name=name;link(o,collection,material)
    for f in o.data.polygons: f.use_smooth=len(f.vertices)==4
    return o

N=int(P['curve_segments']); alpha=math.radians(P['curve_half_angle_deg']); chord=P['front_chord']
A=chord/(2*math.sin(alpha)); B=P['front_bulge']/(1-math.cos(alpha))
def curve(t, inset=0):
    theta=-alpha+2*alpha*t
    x=P['front_center_x']+A*math.sin(theta)
    y=P['curve_end_y']-B*(math.cos(theta)-math.cos(alpha))
    tangent=Vector((A*math.cos(theta),B*math.sin(theta)))
    normal=Vector((tangent.y,-tangent.x)).normalized()
    return (x-normal.x*inset,y-normal.y*inset)

def band(name,z0,z1,inset0,inset1,material,collection=SRC,cap_bottom=True,cap_top=True):
    verts=[]
    for i in range(N+1):
        for inset,z in [(inset0,z0),(inset0,z1),(inset1,z0),(inset1,z1)]:
            x,y=curve(i/N,inset);verts.append((x,y,z))
    faces=[]
    for i in range(N):
        a=4*i;b=4*(i+1)
        faces += [(a,b,b+1,a+1),(a+2,a+3,b+3,b+2)]
        if cap_bottom:faces.append((a,a+2,b+2,b))
        if cap_top:faces.append((a+1,b+1,b+3,a+3))
    faces += [(0,1,3,2),(4*N,4*N+2,4*N+3,4*N+1)]
    o=mesh(name,verts,faces,material,collection)
    for f in o.data.polygons:
        # Smooth only broad exterior and interior curved wall strips.
        if abs(f.normal.z)<.01 and len(f.vertices)==4:f.use_smooth=True
    return o

# Upper portal: only the documented upper-left return and longer right return.
W=P['overall_width']; H=P['overall_height']; ch=P['canopy_height']; cf=P['canopy_front_y']; fw=P['frame_face_width']; fd=P['frame_depth']
box('01 | Wide silver canopy', (0,cf+P['canopy_depth']/2,H-ch/2),(W,P['canopy_depth'],ch))
for side,x,z0 in [('Left upper return',-W/2+fw/2,P['left_frame_bottom']),('Right visible return',W/2-fw/2,P['right_frame_bottom'])]:
    box('02 | '+side,(x,cf+fd/2,(z0+H-ch)/2),(fw,fd,H-ch-z0))
# Broad panel divisions, shallow offsets; no advertising, posters, or surrounding construction.
for k,x in enumerate([-1.72,-.86,0,.86,1.72]):
    box('03 | Canopy panel seam %02d'%k,(x,cf-.0015,H-ch/2),(.007,.003,ch-.025),seam,bevel=0)
for z in [3.42,4.12,4.85,5.53]:
    if z>P['right_frame_bottom']:
        box('03 | Right surround panel seam %.2f'%z,(W/2-fw/2,cf-.0015,z),(fw-.014,.003,.006),seam,bevel=0)
# Projecting underside has two narrow rails but no connecting station structure.
for x in [-1.75,1.72]:
    box('04 | Canopy visible underside rail',(x,cf+P['canopy_depth']/2,H-ch-.035),(.055,P['canopy_depth']-.12,.07),silver_edge)

# Shared curve ensures exact frontage continuity. Adjacent interface caps deliberately omitted.
z0=P['silver_band_bottom'];zi=P['band_interface_z'];zt=P['green_band_top']
lo=band('10 | Bowed silver lower fascia',z0,zi,0,P['silver_shell_thickness'],silver,cap_top=False)
up=band('11 | Bowed pale-green upper band',zi,zt,0,P['green_shell_thickness'],green,cap_bottom=False)
# Tiny rear-facing width transition closes the unequal shell thicknesses without overlapping faces.
verts=[]
for i in range(N+1):
    for inset in [P['green_shell_thickness'],P['silver_shell_thickness']]:
        x,y=curve(i/N,inset);verts.append((x,y,zi))
mesh('12 | Hidden band thickness transition',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(N)],silver,EST)
# Fine lined appearance is explicit original geometry, not photo-derived textures.
for i in range(1,int(P['green_line_count'])+1):
    z=zi+(zt-zi)*i/(int(P['green_line_count'])+1)
    band('13 | Fine horizontal lining %02d'%i,z-.004,z+.004,-.0025,-.0008,green_line)
band('14 | Upper band perimeter rail',zt-.013,zt+.013,-.008,.047,silver_edge)
band('14 | Clean shared band rail',zi-.010,zi+.010,-.009,-.002,silver_edge)
# Vertical divisions stay modest and follow the same plan.
for j,t in enumerate([0,1/6,2/6,3/6,4/6,5/6,1]):
    x,y=curve(t,-.008)
    # Slender post aligned with curve tangent; independent from structural supports.
    o=box('15 | Frontage mullion %02d'%j,(x,y,(zi+zt)/2),(.025,.018,zt-zi),silver_edge,bevel=.002)
    theta=-alpha+2*alpha*t;o.rotation_euler.z=math.atan2(B*math.sin(theta),A*math.cos(theta))
for j,t in enumerate([1/6,2/6,3/6,4/6,5/6]):
    x,y=curve(t,-.0025)
    o=box('16 | Silver fascia panel joint %02d'%j,(x,y,(z0+zi)/2),(.007,.004,zi-z0-.02),seam,bevel=0)
    theta=-alpha+2*alpha*t;o.rotation_euler.z=math.atan2(B*math.sin(theta),A*math.cos(theta))

# Three independently observed support locations, never an inferred mirrored complete system.
s=P['upper_support'];cylinder('20 | Observed upper-left support',s['x'],s['y'],*s['z'],s['diameter']/2)
s=P['lower_right_support'];rs=P['support_red_strip'];r=s['diameter']/2
za=rs['center_z']-rs['height']/2;zb=rs['center_z']+rs['height']/2
cylinder('21 | Lower right support visible below red strip',s['x'],s['y'],s['visible_from_z'],za,r)
cylinder('21 | Lower right support red strip',s['x'],s['y'],za,zb,r,red)
cylinder('21 | Lower right support visible above red strip',s['x'],s['y'],zb,s['z'][1],r)
cylinder('22 | Lower right support hidden foot continuation',s['x'],s['y'],s['z'][0],s['visible_from_z'],r,silver,EST)
# P1 explicitly shows this second LOWER support and red strip (x240–266, y492–545).
s=P['lower_left_support'];r=s['diameter']/2
cylinder('23 | Lower left support visible below red strip',s['x'],s['y'],s['visible_from_z'],za,r)
cylinder('23 | Lower left support red strip',s['x'],s['y'],za,zb,r,red)
cylinder('23 | Lower left support visible above red strip',s['x'],s['y'],zb,s['z'][1],r)
cylinder('24 | Lower left support crowd-hidden continuation',s['x'],s['y'],s['z'][0],s['visible_from_z'],r,silver,EST)

# Upper recess: flat observed aperture only, surrounded by open air, not an invented storey.
y=P['rear_opening_y'];rw=P['rear_opening_width'];rz0,rz1=P['rear_opening_z'];cx=.13;bar=.075
box('30 | Upper aperture left jamb',(cx-rw/2,y,(rz0+rz1)/2),(bar,.08,rz1-rz0),silver_edge)
box('30 | Upper aperture right jamb',(cx+rw/2,y,(rz0+rz1)/2),(bar,.08,rz1-rz0),silver_edge)
for z in [rz0,rz1]:box('30 | Upper aperture horizontal frame',(cx,y,z),(rw+.075,.08,bar),silver_edge)
for x in [cx-rw/6,cx+rw/6]:box('31 | Upper aperture mullion',(x,y,(rz0+rz1)/2),(.055,.08,rz1-rz0),silver_edge)
for i in range(3):
    x=cx-rw/2+(i+.5)*rw/3
    box('32 | Flat upper aperture pane %d'%i,(x,y+.035,(rz0+rz1)/2),(rw/3-.07,.018,rz1-rz0-.075),window,bevel=0)
# No upper rear or lateral box. No deck behind the curved upper band.

# Lower closure is intentionally one removable shallow collection, not a policebox room.
lc=P['lower_closure'];lz0,lz1=lc['z'];ly=lc['y'];lw=lc['width'];lcx=.08
box('40 | Estimated removable lower doorway backing',(lcx,ly+lc['depth']/2,(lz0+lz1)/2),(lw,lc['depth'],lz1-lz0),dark,EST,bevel=.003)
# Quiet facade framing only; no invented hardware, notices, emblems or devices.
for x in [lcx-lw/2,lcx-.72,lcx+.63,lcx+lw/2]:
    box('41 | Estimated lower frame',(x,ly-.018,(lz0+lz1)/2),(.055,.035,lz1-lz0),silver_edge,EST,bevel=.002)
for z in [lz0+.05,lz1-.03]:
    box('41 | Estimated lower horizontal frame',(lcx,ly-.018,z),(lw,.035,.06),silver_edge,EST,bevel=.002)
box('42 | Estimated shallow lower transom',(lcx,ly-.025,lz1-.18),(lw,.05,.24),silver_edge,EST)
th=P['threshold'];box('43 | Provisional masked threshold',(lcx,ly-th['depth']/2,th['height']/2),(th['width'],th['depth'],th['height']),stone,EST,bevel=.003)

# Optional plain identity sign, no exact police emblem or protected sign texture.
sg=P['optional_sign']
if sg['enabled']:
    signz=H-ch/2+.025
    box('50 | Separate plain KOBAN sign',(sg['x'],cf-sg['depth']/2-.018,signz),(sg['width'],sg['depth'],sg['height']),silver_edge)
    box('50 | Plain sign inset',(sg['x'],cf-sg['depth']-.022,signz),(sg['width']-.04,.006,sg['height']-.04),white,bevel=.004)
    cu=bpy.data.curves.new('Plain KOBAN lettering','FONT');cu.body='KOBAN';cu.size=.125;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0008
    o=bpy.data.objects.new('51 | Plain KOBAN lettering, not exact artwork',cu);COL[SRC].objects.link(o)
    o.location=(sg['x'],cf-sg['depth']-.028,signz-.05);o.rotation_euler=(math.pi/2,0,0);cu.materials.append(letters)
    o['component_scope']=SRC;o['estimated_dimensions']=True
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')

# Preserve the unexported editable curve as a revision guide.
cu=bpy.data.curves.new('PARAMETRIC CURVE guide | 24-segment elliptical arc','CURVE');cu.dimensions='3D'
spl=cu.splines.new('POLY');spl.points.add(N)
for i in range(N+1):x,y=curve(i/N);spl.points[i].co=(x,y,zi,1)
guide=bpy.data.objects.new('Curve source guide | excluded export',cu);COL[REVIEW].objects.link(guide);guide.hide_render=True

# Model-only studio. All stages, cameras and labels excluded from GLB.
floor=mat('Review ground only',(.78,.81,.80),0,.9)
box('Review floor',(0,0,-.035),(200,200,.06),floor,REVIEW,bevel=0)
world=bpy.data.worlds.new('Review neutral world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.72,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6

def area(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);COL[REVIEW].objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,3.2))-o.location).to_track_quat('-Z','Y').to_euler()
area('Review key',(-5,-8,10),1250,7)
area('Review fill',(6,-3,7),850,6)
area('Review rim',(1,5,10),1300,5)

cameras={}
def camera(name,loc,target,ortho):
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=ortho;data.lens=50;data.clip_end=300
    o=bpy.data.objects.new(name,data);COL[REVIEW].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cameras[name]=o;return o
camera('front',(0,-17,3.35),(0,0,3.35),8.1)
camera('left_oblique',(-10,-14,8.3),(0,0,3.20),8.6)
camera('right_oblique',(10,-14,8.1),(0,0,3.20),8.6)
camera('top_silhouette',(0,-.1,18),(0,-.1,0),7.4)
camera('confidence',(9,-15,8.3),(0,0,3.25),9.3)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.render.image_settings.color_mode='RGB'
scene.camera=cameras['right_oblique']

# Essential geometric audit of evaluated export objects.
export_objs=list(COL[SRC].objects)+list(COL[EST].objects)
deps=bpy.context.evaluated_depsgraph_get(); bounds=[];zero=[];neg=[];tris=0;verts=0;faces=0;components=[]
for o in export_objs:
    ev=o.evaluated_get(deps);me=ev.to_mesh()
    if not me:continue
    me.calc_loop_triangles();nz=sum(f.area<1e-12 for f in me.polygons)
    if nz:zero.append({'object':o.name,'count':nz})
    for v in me.vertices:bounds.append(o.matrix_world@v.co)
    bm=bmesh.new();bm.from_mesh(me)
    # Signed volume only applies to closed mesh components; open strips are intentional.
    closed=all(e.is_manifold for e in bm.edges)
    volume=bm.calc_volume(signed=True) if closed else None
    if closed and volume is not None and volume < -1e-10:neg.append(o.name)
    components.append({'name':o.name,'scope':o.get('component_scope'), 'vertices':len(me.vertices),'faces':len(me.polygons),'triangles':len(me.loop_triangles),'closed_manifold':closed,'signed_volume_if_closed':volume})
    bm.free();verts+=len(me.vertices);faces+=len(me.polygons);tris+=len(me.loop_triangles);ev.to_mesh_clear()
mins=[min(v[i] for v in bounds) for i in range(3)];maxs=[max(v[i] for v in bounds) for i in range(3)]
# Check original two broad curve surfaces at each shared frontage point, including normals.
curve_joint_error=max((lo.data.vertices[4*i+1].co-up.data.vertices[4*i].co).length for i in range(N+1))
# Analytic outward-facing broad front normals for silver & green surfaces.
outward_dot=[]
for obj in [lo,up]:
    for i in range(N):
        # first face in each segment is front wall; number faces differs with cap flags.
        idx=i*3
        f=obj.data.polygons[idx]
        mid=(i+.5)/N;theta=-alpha+2*alpha*mid
        expected=Vector((B*math.sin(theta),-A*math.cos(theta),0)).normalized()
        outward_dot.append(f.normal.dot(expected))
audit={'asset_id':PARAMS['asset_id'],'status':PARAMS['status'],'blender_version':bpy.app.version_string,'reference_date':'2025-04-09','units':'estimated meters','bounds_blender_xyz':{'min':mins,'max':maxs,'size':[maxs[i]-mins[i] for i in range(3)]},'export_object_count':len(export_objs),'evaluated_vertices':verts,'evaluated_faces':faces,'evaluated_triangles':tris,'zero_area_faces':zero,'negative_volume_closed_objects':neg,'band_front_interface_gap_m':curve_joint_error,'band_interface_overlap_note':'Top cap of lower band and bottom cap of upper band omitted. One rear thickness transition; no overlapping interface caps. Small front rail intentionally covers seam.','minimum_broad_front_normal_dot_outward':min(outward_dot),'source_visible_object_count':len(COL[SRC].objects),'estimated_closure_object_count':len(COL[EST].objects),'components':components}
if zero or neg or min(outward_dot)<.95:raise RuntimeError('Essential mesh validation failed: '+str((zero,neg,min(outward_dot))))

# Only source-visible and estimated closure collections are selected for export.
bpy.ops.object.select_all(action='DESELECT')
for o in export_objs:o.select_set(True)
bpy.context.view_layer.objects.active=lo
scene.camera=cameras['right_oblique']
blend=OUT/(PARAMS['asset_id']+'.blend');glb=OUT/(PARAMS['asset_id']+'.glb')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT',export_yup=True,export_normals=True,export_texcoords=False,export_animations=False)
audit['glb_sha256']=hashlib.sha256(glb.read_bytes()).hexdigest()
(OUT/'mesh_audit.json').write_text(json.dumps(audit,indent=2)+'\n')

if not args.no_render:
    rd=OUT/'renders';rd.mkdir(exist_ok=True)
    for name in ['front','left_oblique','right_oblique','top_silhouette']:
        if name=='top_silhouette' and args.skip_top_render:continue
        scene.camera=cameras[name];scene.render.filepath=str(rd/(name+'.png'));bpy.ops.render.render(write_still=True)
    saved={}
    for o in export_objs:
        saved[o.name]=list(o.data.materials);o.data.materials.clear();o.data.materials.append(orange if o in COL[EST].objects[:] else cyan)
    scene.camera=cameras['confidence'];cam=scene.camera
    def screen_text(body,x,y,size,name):
        cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='LEFT';cu.materials.append(labelmat)
        o=bpy.data.objects.new(name,cu);COL[REVIEW].objects.link(o);o.parent=cam;o.location=(x,y,-10);o.rotation_euler=(0,0,0)
        return o
    text_objs=[screen_text('GEOMETRY SCOPE  /  2025-04-09 REFERENCES',-4.20,4.0,.16,'Confidence title'),screen_text('TEAL: source-visible components, sizes estimated',-4.20,-3.88,.145,'Confidence visible legend'),screen_text('ORANGE: estimated closure / hidden continuations',-4.20,-4.10,.145,'Confidence estimated legend')]
    scene.render.filepath=str(rd/'estimated_regions_confidence.png');bpy.ops.render.render(write_still=True)
    for o in text_objs:bpy.data.objects.remove(o,do_unlink=True)
    for o in export_objs:
        o.data.materials.clear()
        for m in saved[o.name]:o.data.materials.append(m)
    scene.camera=cameras['right_oblique']
print('POLICEBOX_BUILD_COMPLETE '+json.dumps({k:audit[k] for k in ['asset_id','evaluated_triangles','export_object_count','glb_sha256']}))
