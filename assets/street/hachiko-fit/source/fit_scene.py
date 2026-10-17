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
    shell=fit('a29_a8_entrance_shell_2025_v001','a29_a8_entrance_shell_2025_v001.glb',xy,yaw,z)
    # Close the height change to the retained 4.60m canopy with folded flashing.
    # Original north canopy stays fixed; the entrance module is not stretched.
    pale=next(o.data.materials[0] for o in shell if o.type=='MESH' and 'Pale_aluminium' in o.name)
    def local_box(name,u,v,w,d,base,top):
        x,y=xy[0]+co*u-si*v,xy[1]+si*u+co*v
        return box(name,(x,y,(base+top)/2),(w,d,top-base),pale,yaw)
    local_box('A8_roof_infill',0,.075,5.90,9.05,4.015,4.04)
    local_box('A8_north_canopy_transition',0,4.52,5.90,.16,z+3.70,4.61)
    for u in [-2.91,2.91]:
        local_box('A8_side_canopy_transition',u,0,.08,9.12,z+3.70,4.61)
    # Join flashing into the existing aluminium material primitive.
    parts=[o for o in shell if o.type=='MESH' and 'Pale_aluminium' in o.name]
    parts += [o for o in bpy.context.scene.objects if o.name.startswith(('A8_north_canopy','A8_side_canopy','A8_roof_infill'))]
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    record={'status':'normal estimated shell with canopy joints','xy_m':xy,'yaw_deg':yaw,'base_tp_m':z+15,'uniform_scale':1,
            'basis':'official A8/BOX/JR order; southern opening and rounded columns in Aug2025 photos; existing southern roof edge bearing 8.3deg',
            'replacement':'only local x [-2.95,2.95], y <4.6 patch of plaza-kiosk; northern roof, side remnants, BOX and JR retained',
            'adjustment':'complete local roof infill at Web up4.04m plus 0.08m side and 0.16m rear folded closures bridge shell roof to retained canopy at Web up 4.60m; dimensions inferred, no interior or underground; original collision retained'}
elif target == 'louvre':
    # Plane 01 is the broad west-facing patch visible from the statue/lottery zone.
    # This is a bounded equipment-height hypothesis, not an identification of all 14 planes.
    xy=(51.173,-55.148);yaw=-84.073;z=3.0;scale=.6
    fit('station_north_louver_frontage_v001','model/station_north_louver_frontage_v001.glb',xy,yaw,z,scale)
    a=math.radians(yaw);co,si=math.cos(a),math.sin(a)
    back=material('street_fit_louvre_support',(.38,.40,.39),.2)
    def support(name,u,v,w,d,lo,hi):
        box(name,(xy[0]+co*u-si*v,xy[1]+si*u+co*v,(lo+hi)/2),(w,d,hi-lo),back,yaw)
    support('apron',0,-.10,10.14,.12,.20,3.025)
    support('backpan',0,.045,10.14,.10,3.0,5.16)
    for u in [-5.05,5.05]:support('side_return',u,.045,.06,.31,.20,5.16)
    support('head_flashing',0,.045,10.16,.32,5.14,5.20)
    merge_by_material('fit_louvre_')
    record={'status':'normal fitted equipment face','plane_id':'stn_louvre_01','xy_m':xy,'yaw_deg':yaw,'base_tp_m':18,
            'uniform_scale':scale,'dimensions_m':[10.056,.15,2.118],
            'basis':'west-facing existing plane 01, tangent/normal from audit; 2x4 bays in Nov2025 photo below the deck',
            'replacement':'only a 10.056m by 2.118m patch, offset 0.20m in front of old plane and bars; other 13 planes and shared steel remain',
            'adjustment':'pale apron to 3.025m, opaque backing, side returns and head flashing seat the two banks on plane01; original decorative ribs occluded only within this local skin; height and equipment mapping inferred'}
elif target == 'enclosure':
    # Close the footprint around the retained trunk; measured front is preserved.
    centre=(7.4,-45.5);yaw=35;co,si=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    def world(u,v):return centre[0]+u*co-v*si,centre[1]+u*si+v*co
    stone=material('street_fit_enclosure_stone',(.19,.20,.19))
    coping=material('street_fit_enclosure_coping',(.29,.30,.28))
    soil=material('street_fit_enclosure_soil',(.065,.055,.035))
    segments=[((-2.3,-.95),(2.3,-.95)),((2.18,-.83),(2.18,1.53)),((2.3,1.65),(-2.3,1.65)),((-2.18,1.53),(-2.18,-.83))]
    for a,b in segments:
        length=math.dist(a,b);n=math.ceil(length/.4);bearing=yaw+math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
        for i in range(n):
            t=(i+.5)/n;u=a[0]+(b[0]-a[0])*t;v=a[1]+(b[1]-a[1])*t
            x,y=world(u,v);z=height(x,y)-.015
            box('wall',(x,y,z+.25),(length/n-.004,.24,.50),stone,bearing)
            cap=box('coping',(x,y,z+.54),(length/n-.004,.33,.13),coping,bearing)
            cap.rotation_euler.x=math.radians(9)
    # Continuous draped soil surface: adjoining tiles share vertices, without stepped cube seams.
    vs=[];fs=[]
    for j in range(6):
        for i in range(11):
            x,y=world(-2.04+i*4.08/10,-.70+j*2.10/5);vs.append((x,y,height(x,y)+.024))
    for j in range(5):
        for i in range(10):
            k=j*11+i;fs.append((k,k+1,k+12,k+11))
    me=bpy.data.meshes.new('soil');me.from_pydata(vs,[],fs);me.materials.append(soil)
    ob=bpy.data.objects.new('tree_bed',me);bpy.context.collection.objects.link(ob)
    merge_by_material('fit_enclosure_')
    parent=bpy.data.objects.new('fit_enclosure',None);bpy.context.collection.objects.link(parent)
    for ob in list(bpy.context.scene.objects):
        if ob.type=='MESH':ob.parent=parent
    record={'status':'normal complete estimated enclosure','tree_xy_m':centre,'yaw_deg':yaw,
            'outer_size_m':[4.6,2.84],'wall_thickness_m':.24,'wall_height_m':.50,'coping_top_m':.605,
            'front_offset_m':-.95,'rear_offset_m':1.65,'closed_wall_segments_local':segments,
            'basis':'retain photograph-derived front; close sides/back around existing trunk and canopy footprint, rectangular returns inferred; six other trees and statue-side planters retained',
            'estimate':'back/side dimensions and soil are authored reconstruction, not surveyed'}
elif target == 'fence':
    # Four complete bays fitted to the existing posts; no repetition of cropped source geometry.
    start=Vector((.448,-51.639));end=Vector((8.566,-24.557));first,last=2,6
    yaw=math.degrees(math.atan2(end.y-start.y,end.x-start.x))
    white=material('street_fit_white_beam',(.73,.75,.73),.15)
    dark=material('street_fit_beam_fixings',(.08,.09,.09),.5)
    posts=[start.lerp(end,k/15) for k in range(first,last+1)]
    for pa,pb in zip(posts,posts[1:]):
        za,zb=height(*pa),height(*pb)
        a=Vector((pa.x,pa.y,za+.78));b=Vector((pb.x,pb.y,zb+.78))
        ob=box('broad_beam',(a+b)/2,((b-a).length-.006,.08,.28),white)
        ob.rotation_euler=(b-a).to_track_quat('X','Z').to_euler()
    tangent=Vector((math.cos(math.radians(yaw)),math.sin(math.radians(yaw)),0))
    normal=Vector((tangent.y,-tangent.x,0))
    for p in posts:
        z=height(*p);box('post_cover',(p.x,p.y,z+.40),(.075,.08,.88),white,yaw)
        # Join plates cover beam ends; only new front faces, original lower rail remains.
        q=Vector((p.x,p.y,z+.78))+normal*.046
        box('joint_plate',q,(.12,.014,.24),white,yaw)
        for u in [-.04,.04]:
            for dz in [-.07,.07]:
                q=Vector((p.x,p.y,z+.78))+tangent*u+normal*.058+Vector((0,0,dz))
                bpy.ops.mesh.primitive_uv_sphere_add(segments=6,ring_count=3,radius=.0095,location=q)
                bpy.context.object.data.materials.append(dark)
    for p in [posts[0],posts[-1]]:
        z=height(*p);box('end_cap',(p.x,p.y,z+.78),(.018,.10,.30),white,yaw)
    merge_by_material('fit_fence_')
    record={'status':'normal fitted roadside beam','endpoints_xy_m':[list(posts[0]),list(posts[-1])],
            'post_centres_xy_m':[list(p) for p in posts],'yaw_deg':yaw,'bays':last-first,
            'length_m':(posts[-1]-posts[0]).length,'beam_centre_above_ground_m':.78,'beam_height_m':.28,
            'basis':'four existing bays 2-6 of the plaza western boundary rail; July2025 local white beam type; dimensions/assignment estimated',
            'replacement':'top-beam covers, joint plates and closed terminal caps; existing lower rail/posts/collision kept'}
elif target == 'tactile':
    # Connect the actual existing southern tile endpoint around the retained kiosk footprint.
    yellow=material('ground_marking_fit_tactile',(.72,.50,.025))
    old=json.loads((repo/'assets/street/tactile/source/data/stats.json').read_text())
    last=[t for t in old['tiles'] if t['group']=='plaza-south-continuation'][-1]
    direction=Vector(last['direction_xy']);start=Vector(last['centre_xy'])+direction*.15
    angle=math.radians(8.3);co,si=math.cos(angle),math.sin(angle)
    landing=Vector((35.894+si*.95,-51.417-co*.95))
    corner=Vector((35.894+si*3.65,-51.417-co*3.65))
    bend=start+direction*2.1
    points=[start,bend,Vector((44.0,bend.y)),Vector((44.0,corner.y)),corner,landing]
    # Surface meshes, not solid per-ridge boxes: drape every vertex, retain 5mm relief.
    verts=[];faces=[];masks=[];clip_guides=True
    for i,p in enumerate(points[1:]):
        d=(points[i+1]-points[i]).normalized();u=Vector((d.y,-d.x))
        masks.append([p+u*x+d*y for x,y in [(-.3,-.3),(.3,-.3),(.3,.3),(-.3,.3)]])
    def subtract(poly,mask):
        # Split off the outside at each CCW edge; discard only the inner remainder.
        remaining=poly;pieces=[]
        for a,b in zip(mask,mask[1:]+mask[:1]):
            inside=[];outside=[]
            def side(p):return (b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x)
            for p,q in zip(remaining,remaining[1:]+remaining[:1]):
                sp,sq=side(p),side(q)
                (inside if sp>=0 else outside).append(p)
                if (sp<0)!=(sq<0):
                    hit=p+(q-p)*(sp/(sp-sq));inside.append(hit);outside.append(hit)
            if len(outside)>=3:pieces.append(outside)
            remaining=inside
            if len(remaining)<3:break
        return pieces
    def quad(poly,dz):
        pieces=[poly]
        if clip_guides:
            for mask in masks:pieces=[part for piece in pieces for part in subtract(piece,mask)]
        for piece in pieces:
            ids=[]
            for x,y in piece:ids.append(len(verts));verts.append((x,y,height(x,y)+dz))
            faces.append(ids)
    def tile(c,d,length=.30,warning=False):
        across=Vector((d.y,-d.x))
        def q(u,v):return c+across*u+d*v
        quad([q(-.149,-length/2+.001),q(.149,-length/2+.001),q(.149,length/2-.001),q(-.149,length/2-.001)],.003)
        if warning:
            for i in range(5):
                for j in range(5):
                    cc=q((i-2)*.05,(j-2)*.05)
                    # Eight-sided raised dots with sloped edges.
                    ring=[cc+Vector((math.cos(k*math.pi/4),math.sin(k*math.pi/4)))*.011 for k in range(8)]
                    quad(ring,.008)
        else:
            for u in [-.10,-.05,0,.05,.10]:
                quad([q(u-.012,-length/2+.018),q(u+.012,-length/2+.018),q(u+.012,length/2-.018),q(u-.012,length/2-.018)],.008)
    for i,(a,b) in enumerate(zip(points,points[1:])):
        d=(b-a).normalized();length=(b-a).length
        # 0.6m warning junctions at turns; avoid guide overlaps with their footprints.
        begin=0;end=length
        n=max(1,math.ceil((end-begin)/.3));step=(end-begin)/n
        for k in range(n):tile(a+d*(begin+(k+.5)*step),d,step)
    clip_guides=False
    for i,p in enumerate(points[1:]):
        d=(points[i+1]-points[i]).normalized();across=Vector((d.y,-d.x))
        for u in [-.15,.15]:
            for v in [-.15,.15]:tile(p+across*u+d*v,d,warning=True)
    mesh=bpy.data.meshes.new('connected_tactile_surface');mesh.from_pydata(verts,[],faces);mesh.materials.append(yellow)
    ob=bpy.data.objects.new('fit_connected_tactile',mesh);bpy.context.collection.objects.link(ob)
    record={'status':'normal connected estimated guidance route','route_points_xy_m':[list(p) for p in points],
            'source_endpoint':last,'tile_m':.3,'relief_m':.005,'length_m':sum((b-a).length for a,b in zip(points,points[1:])),
            'basis':'existing plaza-south-continuation terminal, north/east/south kiosk boundaries and fitted A8 landing; turns receive warning pads',
            'estimate':'route is reconstructed on the existing sidewalk around BOX and kiosk, not a surveyed guidance map; no NOT_LOCAL kit geometry'}
elif target == 'kerb':
    # Footing/kerb strips at the two side walls of A8; no raised bar across the opening.
    stone=material('ground_kerb_fit_local',(.30,.31,.29))
    xy=(35.25,-47);yaw=8.3;co,si=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    segments=[]
    for u in [-3.03,3.03]:
        for i in range(9):
            v=-4.35+(i+.5)*.6;x,y=xy[0]+co*u-si*v,xy[1]+si*u+co*v
            z=height(x,y);rise=.06*min(1,(i+1)/2)
            box('side_kerb',(x,y,z+rise/2-.012),(.16,.596,rise+.024),stone,yaw)
        segments.append([[xy[0]+co*u-si*v,xy[1]+si*u+co*v] for v in [-4.35,1.05]])
    merge_by_material('fit_kerb_')
    record={'status':'normal local side kerbs','side_segments_xy_m':segments,'width_m':.16,'maximum_rise_m':.06,
            'basis':'junction of fitted A8 side walls and measured pavement; first blocks lower toward open landing',
            'estimate':'local footing dimensions inferred; open 5.8m frontage retained and no road/terrain mesh changed'}
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
if samples:
    record['ground_contact_check']={'successful_samples':len(samples),'min_tp_m':min(p[2] for p in samples),'max_tp_m':max(p[2] for p in samples),'missing':0}
    # Representative contacts; every emitted vertex was queried, not just these samples.
    record['ground_samples_tp_m']=[samples[i] for i in range(0,len(samples),max(1,math.ceil(len(samples)/64)))]
else:record['ground_samples_tp_m']=[]
(out/(target+'.json')).write_text(json.dumps(record,indent=2)+'\n',newline='\n')
