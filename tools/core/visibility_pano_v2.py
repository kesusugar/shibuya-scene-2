# Gate C0 supplement: object-ID panoramas on PLATEAU LOD2 surfaces, one datum, plus a burial check per camera.
#   blender -b -P tools/core/visibility_pano_v2.py -- <records_v2.json> <cameras.json> <out_dir> [width]
# Like visibility_pano.py, but records carry 'polys' (3D rings, datum metres) or a prism ('parts', 'base_z',
# 'height_used'), and camera z is in datum metres. Before rendering, 200 rays from each camera report the nearest
# surface and the share of rays whose first hit is a back face (camera inside a closed shell = buried).
import bpy, bmesh, json, sys, os, math
import numpy as np
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
R = json.load(open(argv[0])); CAMS = json.load(open(argv[1])); OUT = argv[2]; W = int(argv[3]) if len(argv) > 3 else 1440
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene

def emis(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*rgb, 1); e.inputs['Strength'].default_value = 1
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0]); return m

bm = bmesh.new(); mats = []; skipped = 0
def face(vs, i):
    global skipped
    try:
        f = bm.faces.new(vs); f.material_index = i
    except ValueError:
        skipped += 1
for i, r in enumerate(R):
    mats.append(emis(f'id{i+1}', ((i + 1) / 1000.0, 0, 0)))
    if r.get('polys'):
        for ring in r['polys']:
            pts = ring[:-1] if ring[0] == ring[-1] else ring
            if len(pts) >= 3: face([bm.verts.new(p) for p in pts], i)
    else:
        z0 = r.get('base_z', 0.0); h = float(r['height_used'])
        for ring in r['parts']:
            pts = ring[:-1] if ring[0] == ring[-1] else ring
            if len(pts) < 3: continue
            v0 = [bm.verts.new((p[0], p[1], z0)) for p in pts]; v1 = [bm.verts.new((p[0], p[1], z0 + h)) for p in pts]
            face(v1, i)
            for k in range(len(pts)): face((v0[k], v0[(k + 1) % len(pts)], v1[(k + 1) % len(pts)], v1[k]), i)
me = bpy.data.meshes.new('city'); bm.to_mesh(me); bm.free()
for m in mats: me.materials.append(m)
ob = bpy.data.objects.new('city', me); sc.collection.objects.link(ob)
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -0.6)); bpy.context.object.data.materials.append(emis('ground', (0, 1, 0)))
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0
print('faces skipped (degenerate)', skipped)

dg = bpy.context.evaluated_depsgraph_get()
def burial(o):
    n = 200; hits = []; back = 0
    for k in range(n):
        z = 1 - 2 * (k + .5) / n; rr = math.sqrt(1 - z * z); a = k * math.pi * (3 - math.sqrt(5))
        d = Vector((rr * math.cos(a), rr * math.sin(a), z))
        ok, loc, nor, idx, obj, _ = sc.ray_cast(dg, Vector(o), d)
        if ok and obj.name == 'city':
            hits.append((loc - Vector(o)).length)
            if nor.dot(d) > 0: back += 1
    return {'rays': n, 'hits_city': len(hits), 'nearest_m': round(min(hits), 2) if hits else None, 'backface_share': round(back / n, 3)}

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 1; sc.cycles.use_denoising = False
sc.cycles.max_bounces = 0; sc.render.filter_size = 0.01; sc.cycles.pixel_filter_type = 'BOX'
sc.view_settings.view_transform = 'Standard'; sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
sc.render.resolution_x, sc.render.resolution_y = W, W // 2
cam = bpy.data.cameras.new('pano'); cam.type = 'PANO'
if hasattr(cam, 'panorama_type'): cam.panorama_type = 'EQUIRECTANGULAR'
else: cam.cycles.panorama_type = 'EQUIRECTANGULAR'
co = bpy.data.objects.new('pano', cam); sc.collection.objects.link(co); sc.camera = co
H = W // 2; lat = (0.5 - (np.arange(H) + 0.5) / H) * math.pi; wrow = np.cos(lat); total = float(wrow.sum() * W)
col_bearing = ((np.arange(W) + 0.5) / W - 0.5) * 360.0
for c in CAMS:
    pos = (c['x_m'], c['y_m'], c['z_datum_m']); bur = burial(pos)
    co.location = pos; co.rotation_euler = (math.pi / 2, 0, 0)
    path = os.path.join(OUT, f"{c['camera_id']}.exr"); sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path); px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1]
    ids = np.rint(px[:, :, 0] * 1000).astype(np.int32); ids[(px[:, :, 1] > .5) & (ids == 0)] = -1
    np.save(os.path.join(OUT, f"{c['camera_id']}_ids.npy"), ids)
    res = {}
    fwd = None
    if 'view_bearing_deg' in c:   # photo cameras: also the share inside the photo's horizontal field
        dd = (col_bearing - c['view_bearing_deg'] + 180) % 360 - 180; fwd = np.abs(dd) <= c.get('half_hfov_deg', 33)
        ftot = float(wrow.sum() * fwd.sum())
    for k in np.unique(ids[ids > 0]):
        mask = ids == k; share = float((mask * wrow[:, None]).sum() / total)
        sectors = {}
        for s in range(6):
            lo = s * 60; m2 = mask[:, ((col_bearing % 360) >= lo) & ((col_bearing % 360) < lo + 60)]
            ws = float((m2 * wrow[:, None]).sum() / total)
            if ws > 0: sectors[f'{lo:03d}-{lo+60:03d}'] = ws
        e = {'share_of_sphere': share, 'sectors': sectors}
        if fwd is not None: e['share_of_photo_field'] = float((mask[:, fwd] * wrow[:, None]).sum() / ftot)
        res[R[k - 1]['id']] = e
    sky = float(((ids == 0) * wrow[:, None]).sum() / total); ground = float(((ids == -1) * wrow[:, None]).sum() / total)
    json.dump({'camera': c, 'width': W, 'burial_check': bur, 'sky_share': sky, 'ground_share': ground, 'buildings': res},
              open(os.path.join(OUT, f"{c['camera_id']}_coverage.json"), 'w'), indent=0)
    bpy.data.images.remove(img); os.remove(path)
    print('VIEW', c['camera_id'], 'seen', len(res), 'sky', round(sky, 3), 'ground', round(ground, 3), 'burial', bur)
