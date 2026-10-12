"""C-level context of the Core (PLATEAU 2025 LOD2 shells + shared facade materials), Blender 4.2.3.

blender -b --python-exit-code 1 -t 4 -P build_context.py -- context_input.json textures_dir out.glb stats.json

One mesh per (group, material): groups 'core' and 'station' (station side: shape to be checked against 2025-10
photographs). Walls get a facade tile mapped one bay (BAY m) by one storey (STOREY m) from the building's own ground,
so storeys line up around a building; the wall tint is applied by the viewer per material (src/world/context.ts).
"""
import bpy
import bmesh
import json
import sys
import zlib
from pathlib import Path

from mathutils import Vector

src, tex_dir, output, stats_path = sys.argv[sys.argv.index('--') + 1:][:4]
assert bpy.app.version == (4, 2, 3), 'Use Blender 4.2.3 LTS'
D = json.loads(Path(src).read_text())
DATUM = D['datum_tp_m']
BAY, STOREY = 3.2, 3.6
bpy.ops.wm.read_factory_settings(use_empty=True)

MATS = {}


def mat(name, rgb, rough, image=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    if image:
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(str(Path(tex_dir) / image))
        m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    MATS[name] = m


mat('ctx_wall_ribbon_a', (1, 1, 1), 0.5, 'facade_ribbon.png')
mat('ctx_wall_ribbon_b', (1, 1, 1), 0.5, 'facade_ribbon.png')
mat('ctx_wall_punched_a', (1, 1, 1), 0.7, 'facade_punched.png')
mat('ctx_wall_punched_b', (1, 1, 1), 0.7, 'facade_punched.png')
mat('ctx_roof', (0.36, 0.36, 0.35), 0.9)
mat('ctx_structure', (0.50, 0.50, 0.48), 0.85)


def wall_material(b):
    h = b['top_tp'] - b['ground_tp']; k = zlib.crc32(b['plateau_id'].encode()) % 2
    if h > 40:
        return 'ctx_wall_ribbon_' + 'ab'[k]
    if h < 15:
        return 'ctx_wall_punched_' + 'ab'[k]
    return ('ctx_wall_ribbon_', 'ctx_wall_punched_')[zlib.crc32(b['id'].encode()) % 2] + 'ab'[k]


BMS = {}
records = []
for b in D['buildings']:
    wall = wall_material(b) if b['kind'] == 'building' else 'ctx_structure'
    z0 = b['ground_tp'] - DATUM
    nfaces = 0
    for s in b['surfaces']:
        ring = [Vector(p) for p in s['ring']]
        if len(ring) > 3 and (ring[0] - ring[-1]).length < 1e-6:
            ring = ring[:-1]
        if len(ring) < 3:
            continue
        name = (wall if s['kind'] == 'WallSurface' else 'ctx_roof' if b['kind'] == 'building' else 'ctx_structure')
        key = (b['group'], name)
        bm = BMS.setdefault(key, bmesh.new())
        uv = bm.loops.layers.uv.verify()
        try:
            vs = [bm.verts.new(p) for p in ring]
            f = bm.faces.new(vs)
        except ValueError:
            continue
        f.normal_update()
        n = f.normal
        if s['kind'] == 'WallSurface' and abs(n.z) < 0.7 and n.length > 0:
            t = Vector((-n.y, n.x, 0)).normalized()
            for loop in f.loops:
                p = loop.vert.co
                loop[uv].uv = (p.dot(t) / BAY, (p.z - z0) / STOREY)
        else:
            for loop in f.loops:
                p = loop.vert.co
                loop[uv].uv = (p.x / 4, p.y / 4)
        nfaces += 1
    records.append({'id': b['id'], 'plateau_id': b['plateau_id'], 'group': b['group'], 'kind': b['kind'], 'material': wall,
                    'height_m': round(b['top_tp'] - b['ground_tp'], 2), 'faces': nfaces})

for (group, name), bm in BMS.items():
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='EAR_CLIP')
    me = bpy.data.meshes.new(f'{group}__{name}'); bm.to_mesh(me); bm.free()
    me.materials.append(MATS[name])
    ob = bpy.data.objects.new(f'{group}__{name}', me); bpy.context.collection.objects.link(ob)   # no ':' (three.js strips it)

stats = {'blender': bpy.app.version_string, 'datum_tp_m': DATUM, 'bay_m': BAY, 'storey_m': STOREY, 'buildings': records, 'excluded': D['excluded'], 'objects': {}}
for ob in bpy.context.scene.objects:
    ob.data.calc_loop_triangles()
    stats['objects'][ob.name] = {'triangles': len(ob.data.loop_triangles), 'vertices': len(ob.data.vertices)}
stats['triangles'] = sum(o['triangles'] for o in stats['objects'].values())
bpy.ops.export_scene.gltf(filepath=output, export_format='GLB', export_yup=True, export_cameras=False, export_lights=False,
                          export_image_format='AUTO')
Path(stats_path).write_text(json.dumps(stats, ensure_ascii=False, indent=1) + '\n')
print('CONTEXT', len(records), 'buildings,', stats['triangles'], 'triangles,', len(stats['objects']), 'meshes')
