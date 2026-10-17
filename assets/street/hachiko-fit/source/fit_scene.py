"""Fit locally verified delivery GLBs to scene references. Blender coordinates: east/north/up.
Usage: blender -b -P this.py -- <extracted-packages> <target: lottery|a8|louvre|enclosure|finish>
No package scripts are executed. Original building/ground files remain unchanged.
"""
import bpy, bmesh, json, sys, math
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

packages, target = sys.argv[sys.argv.index('--')+1:]
packages = Path(packages)
repo = Path(__file__).resolve().parents[4]
out = repo/'assets/street/hachiko-fit/web'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def clear():
    for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o, do_unlink=True)

def load(path):
    old = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return list(set(bpy.context.scene.objects)-old)

load(repo/'assets/ground/core/web/ground_core.glb')
bm = bmesh.new()
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH' and ob.name.startswith(('ground_sidewalk','ground_island','ground_fill')):
        me = ob.data.copy(); me.transform(ob.matrix_world); bm.from_mesh(me); bpy.data.meshes.remove(me)
ground = BVHTree.FromBMesh(bm); bm.free(); clear()
samples = []
def height(x,y):
    hit = ground.ray_cast(Vector((x,y,40)), Vector((0,0,-1)))[0]
    if hit is None: raise ValueError('no local surface at '+str((x,y)))
    samples.append([x,y,round(hit.z+15,5)])
    return hit.z

def fit(package, filename, xy, yaw, z, scale=1):
    objects = load(packages/package/filename)
    transform = Matrix.Translation(Vector((*xy,z))) @ Matrix.Rotation(math.radians(yaw),4,'Z') @ Matrix.Scale(scale,4)
    for o in objects:
        if o.parent is None: o.matrix_world = transform @ o.matrix_world
    return objects

def clip_facility():
    # Preserve smoking cabinet and the southern/back portion of way/858994297.
    # Cut only its north facade strip, where the candidate's shallow frontage sits.
    for ob in load(repo/'assets/street/plaza-facilities/web/plaza-facilities.glb'):
        if ob.type != 'MESH': continue
        ob.data.transform(ob.matrix_world); ob.matrix_world = Matrix.Identity(4)
        bm = bmesh.new(); bm.from_mesh(ob.data)
        geom = [v for v in bm.verts if 7 < v.co.x < 15 and -66 < v.co.y < -59]
        selected = set(geom)
        fs = [f for f in bm.faces if all(v in selected for v in f.verts)]
        es = list({e for f in fs for e in f.edges})
        bmesh.ops.bisect_plane(bm, geom=geom+es+fs, dist=0.00001,
                              plane_co=(0,-62.9,0), plane_no=(0,1,0))
        remove = [v for v in bm.verts if 7 < v.co.x < 15 and -62.899 < v.co.y < -59]
        bmesh.ops.delete(bm, geom=remove, context='VERTS')
        bm.to_mesh(ob.data); bm.free()

materials={}
def material(name,color,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.9;p.inputs['Metallic'].default_value=metal
    materials[name]=m;return m

def box(name,center,size,mat,yaw=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    ob=bpy.context.object;ob.name=name;ob.scale=size;ob.rotation_euler.z=math.radians(yaw)
    ob.data.materials.append(mat);return ob

def merge_by_material(prefix):
    for mat in list(materials.values()):
        obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.materials) and o.data.materials[0]==mat]
        if not obs:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs:o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=prefix+mat.name

if target == 'lottery':
    xy=(10.90,-61.55); yaw=187.0
    # The retained PLATEAU facade is farther north than the OSM back outline.
    # Seat the shallow front ahead of that face, not inside it. Sample both v002 feet.
    a=math.radians(yaw)
    contacts=[(xy[0]+x*math.cos(a)+.9585*math.sin(a),
               xy[1]+x*math.sin(a)-.9585*math.cos(a)) for x in [-.715,.715]]
    z=min(height(x,y) for x,y in contacts)-0.008
    clip_facility()
    fit('a28_lottery_three_window_frontage_candidate_v002',
        'a28_lottery_three_window_frontage_candidate_v002.glb',xy,yaw,z)
    record={'status':'normal estimated frontage','xy_m':xy,'yaw_deg':yaw,'base_tp_m':z+15,
            'basis':'north long edge of OSM way/858994297; width and low three-window form; official pin used only as a neighbourhood check',
            'replacement':'north facade strip y > -62.9 only; smoking cabinet and southern structure retained'}
elif target == 'a8':
    # Official plan locates A8 immediately east of BOX, with its opening on the south edge.
    # Fit only the southern part of the PLATEAU polygon; keep its north roof and other walls.
    xy=(35.25,-47.00); yaw=8.3; z=height(35.85,-51.42)-.08
    originals=load(repo/'assets/buildings/plaza-kiosk/web/plaza-kiosk.glb')
    a=math.radians(yaw); co,si=math.cos(a),math.sin(a)
    # Excise the shell-sized southern patch from this confirmation variant, not the whole building.
    for ob in originals:
        if ob.type!='MESH':continue
        ob.data.transform(ob.matrix_world); ob.matrix_world=Matrix.Identity(4)
        bm=bmesh.new();bm.from_mesh(ob.data)
        # Three planes bound the replacement: x local [-2.95,2.95], north edge local 4.6.
        for point,normal in [((xy[0]-2.95*co,xy[1]-2.95*si,0),(co,si,0)),
                             ((xy[0]+2.95*co,xy[1]+2.95*si,0),(co,si,0)),
                             ((xy[0]-4.6*si,xy[1]+4.6*co,0),(-si,co,0))]:
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal)
        remove=[]
        for f in bm.faces:
            p=f.calc_center_median();dx,dy=p.x-xy[0],p.y-xy[1]
            if -2.949 < co*dx+si*dy < 2.949 and -si*dx+co*dy <4.599:remove.append(f)
        bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ob.data);bm.free()
    fit('a29_a8_entrance_shell_2025_v001','a29_a8_entrance_shell_2025_v001.glb',xy,yaw,z)
    record={'status':'confirmation preview','xy_m':xy,'yaw_deg':yaw,'base_tp_m':z+15,'uniform_scale':1,
            'basis':'official A8/BOX/JR order; southern opening and rounded columns in Aug2025 photos; existing southern roof edge bearing 8.3deg',
            'replacement':'only local x [-2.95,2.95], y <4.6 patch of plaza-kiosk; northern roof, side remnants, BOX and JR retained',
            'unresolved':'roof width discrepancy and exact shared boundary; no underground or interior; existing collision retained'}
elif target == 'louvre':
    # Plane 01 is the broad west-facing patch visible from the statue/lottery zone.
    # This is a bounded equipment-height hypothesis, not an identification of all 14 planes.
    xy=(51.173,-55.148);yaw=-84.073;z=3.0;scale=.6
    fit('station_north_louver_frontage_v001','model/station_north_louver_frontage_v001.glb',xy,yaw,z,scale)
    record={'status':'confirmation preview','plane_id':'stn_louvre_01','xy_m':xy,'yaw_deg':yaw,'base_tp_m':18,
            'uniform_scale':scale,'dimensions_m':[10.056,.15,2.118],
            'basis':'west-facing existing plane 01, tangent/normal from audit; 2x4 bays in Nov2025 photo below the deck',
            'replacement':'only a 10.056m by 2.118m patch, offset 0.20m in front of old plane and bars; other 13 planes and shared steel remain',
            'unresolved':'exact equipment-to-building correspondence and lower elevation; preview only, no material-wide deletion'}
elif target == 'enclosure':
    # The photographed front coping exists; only model that side and short returns.
    # Do not invent the hidden full perimeter or repeat the old statue-side planter units.
    centre=(7.4,-45.5);yaw=35;co,si=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    def world(u,v):return centre[0]+u*co-v*si,centre[1]+u*si+v*co
    stone=material('street_fit_enclosure_stone',(.19,.20,.19))
    coping=material('street_fit_enclosure_coping',(.29,.30,.28))
    parts=[]
    # A 4.6m visible side set 0.95m toward the statue; rear remains open and explicitly unresolved.
    for i in range(12):
        u=-2.3+(i+.5)*4.6/12;x,y=world(u,-.95);z=height(x,y)-.015
        parts.append(box('wall',(x,y,z+.25),(4.6/12-.006,.24,.50),stone,yaw))
        cap=box('coping',(x,y,z+.54),(4.6/12-.004,.33,.13),coping,yaw)
        cap.rotation_euler.x=math.radians(9);parts.append(cap)
    for u in [-2.18,2.18]:
        x,y=world(u,-.58);z=height(x,y)-.015
        parts.append(box('return',(x,y,z+.25),(.24,.72,.50),stone,yaw))
        parts.append(box('return_cap',(x,y,z+.54),(.33,.72,.13),coping,yaw))
    merge_by_material('fit_enclosure_')
    parent=bpy.data.objects.new('fit_enclosure',None);bpy.context.collection.objects.link(parent)
    for ob in list(bpy.context.scene.objects):
        if ob.type=='MESH':ob.parent=parent
    record={'status':'normal partial enclosure','tree_xy_m':centre,'yaw_deg':yaw,
            'visible_side_length_m':4.6,'wall_thickness_m':.24,'wall_height_m':.50,'coping_top_m':.605,
            'front_offset_m':-.95,'return_length_m':.72,
            'basis':'Nov2025 photo shows a straight granite wall with sloping modular coping in front of trunk; existing tree island and statue provide anchors',
            'unresolved':'back perimeter, hidden branch of enclosure, exact measured endpoints; not a complete ring'}
elif target == 'fence':
    # One complete inferred bay between two existing posts. Do not repeat or stretch the 0.57m crop.
    start=Vector((.448,-51.639));end=Vector((8.566,-24.557))
    pa=start.lerp(end,3/15);pb=start.lerp(end,4/15);yaw=math.degrees(math.atan2(pb.y-pa.y,pb.x-pa.x))
    za,zb=height(*pa),height(*pb)
    white=material('street_fit_white_beam',(.73,.75,.73),.15)
    dark=material('street_fit_beam_fixings',(.08,.09,.09),.5)
    a=Vector((pa.x,pa.y,za+.78));b=Vector((pb.x,pb.y,zb+.78))
    ob=box('single_broad_beam',(a+b)/2,((b-a).length,.08,.28),white)
    ob.rotation_euler=(b-a).to_track_quat('X','Z').to_euler()
    tangent=(b-a).normalized();normal=Vector((tangent.y,-tangent.x,0))
    for p,z in [(pa,za),(pb,zb)]:
        box('post_cover',(p.x,p.y,z+.40),(.075,.08,.88),white,yaw)
        for u in [-.045,.045]:
            for dz in [-.055,.055]:
                q=Vector((p.x,p.y,z+.78))+tangent*u+normal*.045+Vector((0,0,dz))
                bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.0095,location=q)
                bpy.context.object.data.materials.append(dark)
    merge_by_material('fit_fence_')
    record={'status':'confirmation single-bay estimate','endpoints_xy_m':[list(pa),list(pb)],'yaw_deg':yaw,
            'length_m':(pb-pa).length,'beam_centre_above_ground_m':.78,'beam_height_m':.28,
            'basis':'existing rail bay 3-4 of 15 on run (0.448,-51.639) -> (8.566,-24.557); July2025 white beam/joint study informs the broad face only',
            'unresolved':'white-beam-to-rail-run correspondence, exact section and terminals; whole-bay dimensions and post covers are inferred',
            'replacement':'one broad top-beam cover only; existing rail collision/posts/lower bars kept; 0.57m source crop is not repeated'}
elif target == 'tactile':
    # Short, explicitly preview-only landing approach to the fitted A8 opening.
    # Endpoint is inferred from that entrance, not a complete guidance network.
    yellow=material('ground_marking_fit_tactile',(.72,.50,.025))
    angle=math.radians(8.3);co,si=math.cos(angle),math.sin(angle)
    def path_xy(u,v):return 35.894+co*u-si*v,-51.417+si*u+co*v
    for i in range(9):
        v=-3.5+i*.30
        for u in ([0] if i<7 else [-.15,.15]):
            x,y=path_xy(u,v);z=height(x,y)
            box('tactile_base',(x,y,z+.004),(.30,.298,.008),yellow,8.3)
            if i<7:
                for k in [-2,-1,0,1,2]:
                    xx,yy=path_xy(k*.05,v);box('guide_ridge',(xx,yy,z+.012),(.025,.265,.008),yellow,8.3)
            else:
                for k in range(5):
                    for j in range(5):
                        xx,yy=path_xy(u+(k-2)*.05,v+(j-2)*.05)
                        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.011,depth=.005,location=(xx,yy,z+.0105))
                        bpy.context.object.data.materials.append(yellow)
    merge_by_material('fit_tactile_')
    record={'status':'confirmation preview','route_endpoints_xy_m':[path_xy(0,-3.65),path_xy(0,-.95)],
            'yaw_deg':8.3,'tile_m':.3,'warning_size_m':[.6,.6],'basis':'local 2.7m approach follows the fitted A8 opening normal, with a 0.6m warning pad before its landing, on current measured sidewalk',
            'unresolved':'connection to the actual plaza guidance network; NOT_LOCAL delivered guide profile not asserted as a local source'}
elif target == 'finish':
    objects=load(repo/'assets/street/plaza-finish/web/plaza-finish.glb')
    # Use exactly the accepted local paving surface, without another layer or terrain edit.
    h=json.loads((repo/'assets/street/hachiko/source/data/layout.json').read_text())
    cx,cy=h['xy'];a=math.radians(h['yaw_deg']);co,si=math.cos(a),math.sin(a)
    image=bpy.data.images.load(str(repo/'assets/street/hachiko-fit/source/fan-paving.png'))
    for ob in objects:
        if ob.type!='MESH':continue
        for mat in ob.data.materials:
            for node in mat.node_tree.nodes:
                if node.type=='TEX_IMAGE':node.image=image;node.extension='EXTEND'
        for face in ob.data.polygons:
            for li in face.loop_indices:
                p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co
                dx,dy=p.x-cx,p.y-cy;u=co*dx+si*dy;v=-si*dx+co*dy
                ob.data.uv_layers.active.data[li].uv=((u+5.2)/10.4,(v+4)/7)
        ob.name='fit_local_fan_paving'
    record={'status':'normal local paving material replacement','centre_xy_m':[cx,cy],'yaw_deg':35,
            'bounds_local_m':[-5.2,-4,5.2,3],'height_change_m':0,
            'basis':'July095 and Nov2025 show small grey fan-setts around the statue; preserve the existing plaza-finish clipped triangles and UV-fit one continuous local atlas',
            'tile_pitch_m':.10,'joint_width_m':.004,
            'unresolved':'fan centres and individual stones are inferred; the nonseamless delivered sample is not tiled or repeated; no kerb or road-network change'}
else:
    raise ValueError(target)

bpy.ops.export_scene.gltf(filepath=str(out/(target+'.glb')),export_format='GLB',export_yup=True)
record['ground_samples_tp_m']=samples
(out/(target+'.json')).write_text(json.dumps(record,indent=2)+'\n',newline='\n')
