# Gate C0: per-building screen share from 5 street viewpoints, by rendering an object-ID panorama.
#   blender -b -P tools/core/visibility_pano.py -- <buildings.json> <cameras.json> <out_dir> [width]
# Every building is an extruded footprint (PLATEAU/OSM height, see extract_buildings.py) with a flat emission
# colour that encodes its index; the camera is a 360 x 180 degree equirectangular panorama at eye height.
# Output per camera: <id>_ids.npy (index per pixel, 0 = sky, -1 = ground) and <id>_coverage.json
# (solid-angle share of the whole sphere per building, overall and per 60-degree sector).
import bpy, bmesh, json, sys, os, math
import numpy as np
argv = sys.argv[sys.argv.index('--') + 1:]
B = json.load(open(argv[0])); CAMS = json.load(open(argv[1])); OUT = argv[2]; W = int(argv[3]) if len(argv) > 3 else 1440
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene

def emis(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*rgb, 1); e.inputs['Strength'].default_value = 1
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0]); return m

bm = bmesh.new(); mats = []
for i, b in enumerate(B):
    mats.append(emis(f'id{i+1}', ((i + 1) / 1000.0, 0, 0)))
    for ring in b['parts']:
        pts = ring[:-1] if ring[0] == ring[-1] else ring
        if len(pts) < 3: continue
        h = float(b['height_used'])
        v0 = [bm.verts.new((p[0], p[1], 0.0)) for p in pts]; v1 = [bm.verts.new((p[0], p[1], h)) for p in pts]
        try:
            fs = [bm.faces.new(v1)] + [bm.faces.new((v0[k], v0[(k + 1) % len(pts)], v1[(k + 1) % len(pts)], v1[k])) for k in range(len(pts))]
        except ValueError:
            continue
        for f in fs: f.material_index = i
me = bpy.data.meshes.new('city'); bm.to_mesh(me); bm.free()
for m in mats: me.materials.append(m)
ob = bpy.data.objects.new('city', me); sc.collection.objects.link(ob)
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -0.05)); bpy.context.object.data.materials.append(emis('ground', (0, 1, 0)))
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 1; sc.cycles.use_denoising = False
sc.cycles.max_bounces = 0; sc.render.filter_size = 0.01; sc.cycles.pixel_filter_type = 'BOX'
sc.view_settings.view_transform = 'Standard'; sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
sc.render.resolution_x, sc.render.resolution_y = W, W // 2
cam = bpy.data.cameras.new('pano'); cam.type = 'PANO'
if hasattr(cam, 'panorama_type'): cam.panorama_type = 'EQUIRECTANGULAR'
else: cam.cycles.panorama_type = 'EQUIRECTANGULAR'
co = bpy.data.objects.new('pano', cam); sc.collection.objects.link(co); sc.camera = co

H = W // 2; lat = (0.5 - (np.arange(H) + 0.5) / H) * math.pi; wrow = np.cos(lat)          # row weight = solid angle
total = float(wrow.sum() * W)
for c in CAMS:
    co.location = (c['x_m'], c['y_m'], c['z_m'])
    co.rotation_euler = (math.pi / 2, 0, 0)        # optical axis north (+Y), up +Z; image centre = bearing 0
    path = os.path.join(OUT, f"{c['camera_id']}.exr"); sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path); px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1]
    ids = np.rint(px[:, :, 0] * 1000).astype(np.int32); ids[(px[:, :, 1] > .5) & (ids == 0)] = -1
    np.save(os.path.join(OUT, f"{c['camera_id']}_ids.npy"), ids)
    # bearing of each column: centre = 0 (north); Blender equirect longitude grows to the LEFT, so east is right of centre
    col_bearing = ((np.arange(W) + 0.5) / W - 0.5) * 360.0
    res = {}
    for k in np.unique(ids[ids > 0]):
        mask = ids == k; share = float((mask * wrow[:, None]).sum() / total)
        cols = np.where(mask.any(axis=0))[0]
        sectors = {}
        for s in range(6):
            lo = s * 60; m2 = mask[:, ((col_bearing % 360) >= lo) & ((col_bearing % 360) < lo + 60)]
            ws = float((m2 * wrow[:, None]).sum() / total)
            if ws > 0: sectors[f'{lo:03d}-{lo+60:03d}'] = ws
        res[B[k - 1]['id']] = {'share_of_sphere': share, 'sectors': sectors, 'max_elev_deg': float(np.degrees(lat[np.where(mask.any(axis=1))[0].min()]))}
    sky = float(((ids == 0) * wrow[:, None]).sum() / total); ground = float(((ids == -1) * wrow[:, None]).sum() / total)
    json.dump({'camera': c, 'width': W, 'sky_share': sky, 'ground_share': ground, 'buildings': res}, open(os.path.join(OUT, f"{c['camera_id']}_coverage.json"), 'w'), indent=0)
    bpy.data.images.remove(img); os.remove(path)
    print('VIEW', c['camera_id'], 'buildings seen', len(res), 'sky', round(sky, 3), 'ground', round(ground, 3))
