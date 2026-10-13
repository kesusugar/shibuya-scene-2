# C2a: builds the Core ground GLB from ground_input.json (prepare_ground.py). Blender 4.2.3 LTS, headless.
#   blender -b -P build_ground.py -- <ground_input.json> <out.glb> <stats.json>
# Plan metres (X east, Y north), heights in the common datum: z = T.P. - 15.000 (docs/core/C2A_PLAN.md).
# Objects: ground_road, ground_intersection, ground_sidewalk (+ islands), ground_kerb, ground_marking, ground_fill.
# Sidewalks are densified (edges <= 1.5 m) and lifted by the kerb height, dropping to the low kerb at crosswalk
# landings; kerb faces are built where a sidewalk edge meets the carriageway, short skirts elsewhere hide seams.
# Optional northern and Hachiko plaza paving colour atlases; source geometry/height construction stays unchanged.
import bpy, bmesh, json, sys, math, struct
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from paving_boundary import partition

argv = sys.argv[sys.argv.index('--') + 1:]
src, out_glb, out_stats = argv[:3]
D = json.load(open(src)); PR = D['params']; DATUM = 15.0
config = Path(argv[3]) if len(argv)>3 else Path(__file__).resolve().parents[1]/'data/paving_layout.json'
PAVING = json.loads(config.read_text()) if config.is_file() else None
plaza_config = Path(argv[4]) if len(argv)>4 else Path(__file__).resolve().parents[1]/'data/plaza_paving_layout.json'
PLAZA = json.loads(plaza_config.read_text()) if plaza_config.is_file() else None
KH, KL, LF, LR = PR['kerb_height_m'], PR['kerb_low_m'], PR['landing_flat_m'], PR['landing_ramp_m']
bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, rgb, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    m.use_backface_culling = False; return m
# linear-space flat colours; placeholders until the C3 material pass
MAT = {'road': material('ground_asphalt', (0.045, 0.045, 0.048), 0.85), 'intersection': material('ground_asphalt_intersection', (0.05, 0.05, 0.053), 0.85),
       'sidewalk': material('ground_sidewalk', (0.30, 0.28, 0.25), 0.9), 'island': material('ground_island', (0.24, 0.27, 0.21), 0.9),
       'kerb': material('ground_kerb', (0.42, 0.40, 0.37), 0.85), 'marking': material('ground_marking', (0.80, 0.80, 0.77), 0.6),
       'fill': material('ground_fill_provisional', (0.22, 0.18, 0.26), 0.95)}
if PAVING:
    MAT['pavers'] = material('ground_sidewalk_pavers', (0.30, 0.28, 0.25), 0.9)
    m=MAT['pavers']; tex=m.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str((config.parent/PAVING['texture']).resolve()))
    tex.image.colorspace_settings.name='sRGB';tex.extension='REPEAT'
    tint=m.node_tree.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY'
    tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.30,.28,.25,1)
    m.node_tree.links.new(tex.outputs['Color'],tint.inputs[1])
    m.node_tree.links.new(tint.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])

if PLAZA:
    MAT['plaza'] = material('ground_sidewalk_plaza_pavers', (.30,.28,.25), .9)
    m=MAT['plaza'];tex=m.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str((plaza_config.parent/PLAZA['texture']).resolve()))
    tex.image.colorspace_settings.name='sRGB';tex.extension='REPEAT'
    tint=m.node_tree.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY'
    tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.30,.28,.25,1)
    m.node_tree.links.new(tex.outputs['Color'],tint.inputs[1])
    m.node_tree.links.new(tint.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])


def mesh_from(name, polys, zf, mat):
    bm = bmesh.new()
    for ring in polys:
        vs = [bm.verts.new((p[0], p[1], zf(p))) for p in ring]
        try: bm.faces.new(vs)
        except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < 0: f.normal_flip()
    return bm

def finish(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat); ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob); return ob

tp = lambda p: p[2] - DATUM
S = D['surfaces']
bm_road = mesh_from('road', [s['ring'] for s in S if s['class'] == 'road'], tp, MAT['road'])
bm_int = mesh_from('intersection', [s['ring'] for s in S if s['class'] == 'intersection'], tp, MAT['intersection'])
# carriageway surface for sampling (road + intersection, unlifted)
cw_bm = bmesh.new()
for b in (bm_road, bm_int):
    tmp = bpy.data.meshes.new('tmp'); b.to_mesh(tmp); cw_bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
cw_bvh = BVHTree.FromBMesh(cw_bm)
def road_z(x, y):
    hit = cw_bvh.ray_cast(Vector((x, y, 100.0)), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else None

# sidewalks and islands: densify, then lift by the kerb profile
bm_walk = mesh_from('sidewalk', [s['ring'] for s in S if s['class'] in ('sidewalk', 'island')], tp, MAT['sidewalk'])
island_faces = set()
for _ in range(10):
    long_e = [e for e in bm_walk.edges if e.calc_length() > 1.5]
    if not long_e: break
    bmesh.ops.subdivide_edges(bm_walk, edges=long_e, cuts=1, use_grid_fill=False)
    bmesh.ops.triangulate(bm_walk, faces=bm_walk.faces[:])
landings = [np.array(b) for b in D['landings']]
def dist_to_band(x, y):
    best = 1e9
    for poly in landings:
        n = len(poly); inside = False
        for i in range(n):
            x1, y1 = poly[i]; x2, y2 = poly[i - 1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: inside = not inside
            ex, ey = x2 - x1, y2 - y1; L = ex * ex + ey * ey or 1
            t = max(0, min(1, ((x - x1) * ex + (y - y1) * ey) / L)); best = min(best, math.hypot(x - x1 - t * ex, y - y1 - t * ey))
        if inside: return 0.0
    return best
def kerb(x, y):
    d = dist_to_band(x, y)
    if d <= LF: return KL
    if d >= LF + LR: return KH
    return KL + (KH - KL) * (d - LF) / LR
for v in bm_walk.verts: v.co.z += kerb(v.co.x, v.co.y)
# island faces keep their own material: tag by centroid inside an island ring
isl = [np.array([(p[0], p[1]) for p in s['ring']]) for s in S if s['class'] == 'island']
def in_island(x, y):
    for poly in isl:
        n = len(poly); c = False
        for i in range(n):
            x1, y1 = poly[i]; x2, y2 = poly[i - 1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
        if c: return True
    return False
for f in bm_walk.faces:
    c = f.calc_center_median(); f.material_index = 1 if in_island(c.x, c.y) else 0

paving_faces=0; paving_area=0.0
if PAVING:
    # A separate material limits the atlas to the provisional north-area mask.
    # UVs use plan metres, so slopes and irregular triangles never stretch the block scale.
    uv=bm_walk.loops.layers.uv.verify();a=math.radians(PAVING['yaw_deg']);co,si=math.cos(a),math.sin(a)
    px=PAVING['tile_size_m'][0]*PAVING['atlas_tiles'][0]
    py=PAVING['tile_size_m'][1]*PAVING['atlas_tiles'][1]
    x0,y0,x1,y1=PAVING['bounds_xy_m']
    for f in bm_walk.faces:
        c=f.calc_center_median()
        if x0<=c.x<=x1 and y0<=c.y<=y1:
            f.material_index=2;paving_faces+=1;paving_area+=f.calc_area()
        for loop in f.loops:
            x,y=loop.vert.co.x,loop.vert.co.y
            loop[uv].uv=((co*x+si*y)/px,(-si*x+co*y)/py)

# kerb faces (sidewalk edge over carriageway) and skirts (all other open edges), built from the lifted edge
bm_kerb = bmesh.new(); kerb_len = 0.0; skirt_len = 0.0
def add_quad(bm, a, b, za, zb):
    vs = [bm.verts.new((a.x, a.y, a.z)), bm.verts.new((b.x, b.y, b.z)), bm.verts.new((b.x, b.y, zb)), bm.verts.new((a.x, a.y, za))]
    bm.faces.new(vs)
for e in [e for e in bm_walk.edges if len(e.link_faces) == 1]:
    a, b = e.verts[0].co.copy(), e.verts[1].co.copy(); f = e.link_faces[0]
    mid = (a + b) / 2; c = f.calc_center_median(); d = Vector((mid.x - c.x, mid.y - c.y, 0))
    if d.length < 1e-6: continue
    d.normalize(); probe = mid + d * 0.25
    rz = road_z(probe.x, probe.y)
    if rz is not None:
        za = road_z(a.x + d.x * 0.05, a.y + d.y * 0.05); zb = road_z(b.x + d.x * 0.05, b.y + d.y * 0.05)
        add_quad(bm_kerb, a, b, za if za is not None else rz, zb if zb is not None else rz); kerb_len += (a - b).length
    else:
        add_quad(bm_kerb, a, b, a.z - 0.3, b.z - 0.3); skirt_len += (a - b).length
for b_ in (bm_road, bm_int):   # carriageway edges with nothing beside them: short skirts
    for e in [e for e in b_.edges if len(e.link_faces) == 1]:
        a, b = e.verts[0].co.copy(), e.verts[1].co.copy(); add_quad(bm_kerb, a, b, a.z - 0.3, b.z - 0.3)

# zebra bars draped on the carriageway (+12 mm)
bars = [bar for c in D['crosswalks'] for bar in c['bars']]
def drape(p):
    z = road_z(p[0], p[1]); return (z if z is not None else 0.0) + 0.012
bm_mark = mesh_from('marking', bars, drape, MAT['marking'])

# provisional fill at sidewalk level: nearest lifted sidewalk vertex, else nearest carriageway + kerb; 1 cm lower
kd = KDTree(len(bm_walk.verts))
for i, v in enumerate(bm_walk.verts): kd.insert((v.co.x, v.co.y, 0), i)
kd.balance(); wz = [v.co.z for v in bm_walk.verts]
def fill_z(p):
    co, i, dist = kd.find((p[0], p[1], 0))
    if i is not None and dist < 30: return wz[i] - 0.01
    z = road_z(p[0], p[1]); return (z + KH if z is not None else 0.15) - 0.01
bm_fill = mesh_from('fill', D['fill'], fill_z, MAT['fill'])
for e in [e for e in bm_fill.edges if len(e.link_faces) == 1]:
    a, b = e.verts[0].co.copy(), e.verts[1].co.copy(); add_quad(bm_kerb, a, b, a.z - 0.3, b.z - 0.3)
for f in bm_kerb.faces: f.normal_update()

# Partition only the walking mesh after kerbs/fill have been built from the
# original edges: new material seams must never change their geometry/heights.
plaza_faces=0;plaza_area=0.0;boundary_split_faces=0
if PLAZA:
    polygon=PLAZA['polygon_xy_m']
    x0=min(p[0] for p in polygon);x1=max(p[0] for p in polygon)
    y0=min(p[1] for p in polygon);y1=max(p[1] for p in polygon)
    uv=bm_walk.loops.layers.uv.verify()
    vertices={}
    def vertex(p):
        key=tuple(round(float(c),9) for c in p)
        if key not in vertices:vertices[key]=bm_walk.verts.new(p)
        return vertices[key]
    new_faces=[]
    for face in list(bm_walk.faces):
        points=[tuple(v.co) for v in face.verts]
        if max(p[0] for p in points)<x0 or min(p[0] for p in points)>x1 or max(p[1] for p in points)<y0 or min(p[1] for p in points)>y1:continue
        pieces=partition(points,polygon)
        if len(pieces)==1:
            if pieces[0][1]:face.material_index=3 if PAVING else 2
            continue
        boundary_split_faces+=1;old_material=face.material_index
        # Preserve coincident source triangles independently; do not weld them or change their heights.
        vertices.clear()
        bmesh.ops.delete(bm_walk,geom=[face],context='FACES_ONLY')
        for piece,inside in pieces:
            for j in range(1,len(piece)-1):
                vs=[vertex(p) for p in (piece[0],piece[j],piece[j+1])]
                if len(set(vs))<3:continue
                f=bm_walk.faces.new(vs)
                f.material_index=(3 if PAVING else 2) if inside else old_material
                new_faces.append(f)
    a=math.radians(PLAZA['yaw_deg']);co,si=math.cos(a),math.sin(a)
    plaza_px,plaza_py=[size*count for size,count in zip(PLAZA['tile_size_m'],PLAZA['atlas_tiles'])]
    ox,oy=PLAZA['origin_xy_m']
    # Restore the original north/world UV for newly split, untextured pieces.
    if PAVING:
        na=math.radians(PAVING['yaw_deg']);nc,ns=math.cos(na),math.sin(na)
        for f in new_faces:
            for loop in f.loops:
                x,y=loop.vert.co.x,loop.vert.co.y
                loop[uv].uv=((nc*x+ns*y)/px,(-ns*x+nc*y)/py)
    for f in bm_walk.faces:
        if f.material_index!=(3 if PAVING else 2):continue
        plaza_faces+=1;plaza_area+=f.calc_area()
        for loop in f.loops:
            x,y=loop.vert.co.x-ox,loop.vert.co.y-oy
            loop[uv].uv=((co*x+si*y)/plaza_px,(-si*x+co*y)/plaza_py)
    bm_walk.normal_update()

objs = {'ground_road': finish('ground_road', bm_road, MAT['road']), 'ground_intersection': finish('ground_intersection', bm_int, MAT['intersection'])}
w = finish('ground_sidewalk', bm_walk, MAT['sidewalk']); w.data.materials.append(MAT['island']); objs['ground_sidewalk'] = w
if PAVING: w.data.materials.append(MAT['pavers'])
if PLAZA: w.data.materials.append(MAT['plaza'])
objs['ground_kerb'] = finish('ground_kerb', bm_kerb, MAT['kerb'])
objs['ground_marking'] = finish('ground_marking', bm_mark, MAT['marking'])
objs['ground_fill'] = finish('ground_fill', bm_fill, MAT['fill'])
cw_bm.free()

stats = {'params': PR, 'datum_tp_m': DATUM, 'objects': {}, 'kerb_length_m': round(kerb_len, 1), 'skirt_length_m': round(skirt_len, 1)}
for n, o in objs.items():
    zs = [v.co.z for v in o.data.vertices]
    stats['objects'][n] = {'triangles': sum(len(p.vertices) - 2 for p in o.data.polygons), 'vertices': len(o.data.vertices),
                           'z_min': round(min(zs), 3) if zs else None, 'z_max': round(max(zs), 3) if zs else None}
stats['triangles_total'] = sum(v['triangles'] for v in stats['objects'].values())
if PAVING:
    stats['paving']={'status':PAVING['status'],'faces':paving_faces,'area_m2':round(paving_area,2),'tile_size_m':PAVING['tile_size_m'],'atlas_period_m':[px,py],'bounds_xy_m':PAVING['bounds_xy_m'],'yaw_deg':PAVING['yaw_deg'],'joint_width_m':PAVING['joint_width_m'],'joint_level':PAVING['joint_level']}
if PLAZA:
    stats['plaza_paving']={**PLAZA,'faces':plaza_faces,'area_m2':round(plaza_area,2),'atlas_period_m':[plaza_px,plaza_py],'boundary_split_faces':boundary_split_faces,'boundary_method':'polygon edge partition; interpolated original triangle heights'}
bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB', export_yup=True, export_apply=True, export_normals=True,
                          export_texcoords=bool(PAVING or PLAZA), export_materials='EXPORT', export_extras=False)
if PAVING or PLAZA:
    # Blender's image/multiply graph is not always gathered as a glTF colour factor.
    # Keep the portable asset tint consistent with the Blender shader and the shared web look.
    data=Path(out_glb).read_bytes();magic,version,_=struct.unpack('<III',data[:12])
    length,kind=struct.unpack('<II',data[12:20]);doc=json.loads(data[20:20+length])
    for m in doc['materials']:
        if m['name'] in ('ground_sidewalk_pavers','ground_sidewalk_plaza_pavers'):m['pbrMetallicRoughness']['baseColorFactor']=[.30,.28,.25,1]
    encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
    rest=data[20+length:];total=20+len(encoded)+len(rest)
    Path(out_glb).write_bytes(struct.pack('<III',magic,version,total)+struct.pack('<II',len(encoded),kind)+encoded+rest)
json.dump(stats, open(out_stats, 'w'), indent=1)
print('GROUND', json.dumps(stats))
