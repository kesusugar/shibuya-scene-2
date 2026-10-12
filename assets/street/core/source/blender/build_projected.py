"""Experimental photo-derived furniture, clearly amber and separate from the normal asset.
blender -b --python-exit-code 1 -P build_projected.py -- projections.json out.glb out_metadata.json
Only observed visible bases with actual ground intersections are exported. All placements remain provisional.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

source, output, metadata = sys.argv[sys.argv.index('--') + 1:][:3]
D = json.loads(Path(source).read_text())
assert bpy.app.version == (4, 2, 3)
bpy.ops.wm.read_factory_settings(use_empty=True)
M = {}


def material(name, rgb, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = 0.5
    M[name] = m


material('street_provisional_pole', (0.8, 0.28, 0.025), 0.4)
material('street_lamp_glass', (0.9, 0.86, 0.72))
material('street_signal_body', (0.025, 0.03, 0.035))
material('street_signal_green', (0.03, 0.6, 0.2))
material('street_sign_blue', (0.025, 0.12, 0.6))
material('street_sign_red', (0.8, 0.02, 0.025))


def finish(ob, name):
    ob.data.materials.append(M[name]); return ob


def rod(a, b, radius, name, vertices=12):
    a, b = Vector(a), Vector(b); d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=(a + b) / 2)
    ob = bpy.context.object; ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return finish(ob, name)


def box(center, size, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object; ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, name)


lights = []; rendered = []
rows = {r['id']: r for r in D['observations']}
for row in D['observations']:
    if 'point' not in row or not row.get('ground_base_visible'): continue
    if row['kind'] == 'guardrail_endpoint': continue
    x, y = row['point']; z = row['anchor_tp'] - 15; h = row['height_m']
    rod((x, y, z - 0.08), (x, y, z + h), 0.075, 'street_provisional_pole')
    rod((x, y, z - 0.08), (x, y, z + 0.45), 0.2, 'street_provisional_pole')
    if row['kind'] in ('lamp', 'lamp_signal'):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.24, location=(x, y, z + h - 0.4))
        finish(bpy.context.object, 'street_lamp_glass')
        # Bell profile read from P01; shared P03 profile and the P02 generic head remain provisional.
        if row['id'] == 'P02':
            box((x, y, z + h - 0.1), (0.6, 0.3, 0.18), 'street_provisional_pole')
        else:
            profile = [(0, .34), (.15, .31), (.34, .25), (.48, .17), (.56, .10), (.62, .03)]
            verts = [(x + radius * math.cos(j * 2 * math.pi / 24),
                      y + radius * math.sin(j * 2 * math.pi / 24), z + h - .4 + dz)
                     for dz, radius in profile for j in range(24)]
            faces = [(k*24+j, k*24+(j+1)%24, (k+1)*24+(j+1)%24, (k+1)*24+j)
                     for k in range(len(profile)-1) for j in range(24)]
            me = bpy.data.meshes.new('bell_profile'); me.from_pydata(verts, [], faces)
            cap = bpy.data.objects.new('bell_profile', me); bpy.context.collection.objects.link(cap)
            for polygon in me.polygons: polygon.use_smooth = True
            finish(cap, 'street_provisional_pole')
        lights.append({'id': row['id'], 'position': [x, z + h - 0.45, -y], 'intensity_cd': 1800,
                       'status': 'provisional', 'basis': 'photo-projection; estimated height and intensity',
                       'pixel_error_ground_radius_m': row['pixel_error_ground_radius_m']})
        if row['kind'] == 'lamp_signal':
            t = Vector((6.5 - x, -2 - y, 0)).normalized()
            end = Vector((x, y, z + 3.2)) + 1.6 * t
            rod((x, y, z + 3.2), end, 0.045, 'street_signal_body')
            box(end, (0.32, 0.24, 0.65), 'street_signal_body')
            # Original walk-phase pictogram: head, torso, arms and legs. No traffic simulation.
            center = end + Vector((0, -.14, -.08))
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=.025, location=center + Vector((0, 0, .10)))
            finish(bpy.context.object, 'street_signal_green')
            def human(a, b):
                rod(center + Vector((a[0], 0, a[1])), center + Vector((b[0], 0, b[1])), .012, 'street_signal_green', 6)
            human((0,.065), (0,-.02))
            human((0,.04), (-.055,.0)); human((0,.04), (.05,.015))
            human((0,-.02), (-.045,-.105)); human((0,-.02), (.05,-.085))
    elif row['kind'] == 'sign':
        for i in range(2):
            center = (x, y, z + h - i * 0.7)
            ob = rod((x, y - 0.04, center[2]), (x, y + 0.04, center[2]), 0.32, 'street_sign_red', 24)
            rod((x, y - 0.05, center[2]), (x, y - 0.065, center[2]), 0.265, 'street_sign_blue', 24)
            slash = box((x, y - 0.085, center[2]), (0.62, 0.03, 0.055), 'street_sign_red')
            slash.rotation_euler.y = -math.pi / 4
            if i == 0:
                other = box((x, y - .085, center[2]), (.62, .03, .055), 'street_sign_red')
                other.rotation_euler.y = math.pi / 4
    rendered.append(row['id'])

a, b = rows['R01a'], rows['R01b']
if 'point' in a and 'point' in b:
    A = Vector((*a['point'], a['anchor_tp'] - 15)); B = Vector((*b['point'], b['anchor_tp'] - 15))
    for i in range(4):
        p = A.lerp(B, i / 3)
        rod(p - Vector((0, 0, 0.08)), p + Vector((0, 0, 1.0)), 0.055, 'street_provisional_pole')
    for h in (0.45, 0.9):
        rod(A + Vector((0, 0, h)), B + Vector((0, 0, h)), 0.055, 'street_provisional_pole')
    # The photograph shows fan-shaped inserts. Panel count/thickness are still estimated.
    for panel in range(3):
        a0 = A.lerp(B, panel / 3); b0 = A.lerp(B, (panel + 1) / 3)
        center = a0.lerp(b0, .5) + Vector((0, 0, .4))
        for j in range(5):
            target = a0.lerp(b0, j / 4) + Vector((0, 0, .85))
            rod(center, target, .025, 'street_provisional_pole', 8)
    rendered.append('R01')

for name in M:
    bpy.ops.object.select_all(action='DESELECT')
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.data.materials and o.data.materials[0].name == name]
    for ob in objs: ob.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); bpy.context.object.name = name

bpy.ops.export_scene.gltf(filepath=output, export_format='GLB', export_yup=True)
Path(metadata).write_text(json.dumps({'status': 'experimental_only', 'source': source, 'photo': D['photo'],
                                     'camera_status': D['camera_status'], 'camera_validation': D.get('camera_validation'),
                                     'camera': {**D['camera'], 'fpx': D['camera']['H'] / 2 / math.tan(math.radians(D['camera']['vfov']) / 2)}, 'light_points': lights, 'rendered_ids': rendered,
                                     'geometry_notes': 'P01 bell silhouette, two different regulation signs, pedestrian pictogram and fan railing read from the photo; P02 lamp head/type, P03 shared cap, dimensions and light output remain provisional',
                                     'not_rendered': [r for r in D['observations'] if 'point' not in r]}, ensure_ascii=False, indent=2) + '\n')
print('EXPERIMENTAL', rendered, 'lights', len(lights))
