"""One reference-informed wall monitor. Blender 4.2.3; no external assets.
Usage: blender -b -t 2 --python generate.py -- /absolute/output/directory
Add --skip-render after the output directory to regenerate only the model.
Metres, Blender Z-up, front -Y, bottom-centre origin. No scene placement.
"""
import bpy
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = Path(args[0]).resolve() if args and not args[0].startswith('--') else HERE
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'renders').mkdir(exist_ok=True)
SKIP_RENDER = '--skip-render' in args
NAME = 'shibu_hachi_counter_wall_monitor'
utc = lambda: datetime.now(timezone.utc).isoformat()
started = time.perf_counter()
stages = {'generation_started_utc': utc(), 'blender_version': bpy.app.version_string}
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def material(name, color, roughness):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1.0)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = 0.0
    p.inputs['IOR'].default_value = 1.48
    return m

shell_mat = material('Charcoal polymer bezel and inferred rear', (0.010, 0.011, 0.012), 0.36)
screen_mat = material('Neutral black inactive display, no image or emission', (0.0035, 0.004, 0.0045), 0.22)
objects = []

def rounded_rectangle(w, h, r, zc, y, segments=5):
    """Counterclockwise in X/Z; identical corner sampling for connected loops."""
    points = []
    for cx, cz, start in [(w/2-r, zc+h/2-r, 0),
                          (-w/2+r, zc+h/2-r, 90),
                          (-w/2+r, zc-h/2+r, 180),
                          (w/2-r, zc-h/2+r, 270)]:
        for i in range(segments+1):
            a = math.radians(start + i*90/segments)
            points.append((cx+r*math.cos(a), y, cz+r*math.sin(a)))
    return points

def loop_shell(name, loops, mat, close_ends=False):
    verts = [v for loop in loops for v in loop]
    n = len(loops[0])
    faces = []
    pairs = list(zip(range(len(loops)-1), range(1, len(loops))))
    if not close_ends:
        pairs.append((len(loops)-1, 0))
    for a,b in pairs:
        for i in range(n):
            j = (i+1) % n
            faces.append((a*n+i, a*n+j, b*n+j, b*n+i))
    if close_ends:
        faces.extend([tuple(reversed(range(n))), tuple((len(loops)-1)*n+i for i in range(n))])
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    objects.append(obj)
    return obj

# Continuous frame, not four intersecting bars. The 3 mm outer chamfer and
# 6 mm aperture return preserve the real thin rim and recessed panel silhouette.
bezel = loop_shell('Continuous narrow bezel with recessed inner return', [
    rounded_rectangle(1.550, .900, .006, .450, .008),
    rounded_rectangle(1.550, .900, .006, .450, -.032),
    rounded_rectangle(1.544, .894, .004, .450, -.035),
    rounded_rectangle(1.510, .851125, .0016, .4515625, -.035),
    rounded_rectangle(1.507, .848125, .0007, .4515625, -.029),
    rounded_rectangle(1.507, .848125, .0007, .4515625, .008),
], shell_mat)
bezel['evidence'] = 'Narrow dark perimeter directly visible; widths, chamfer and recess estimated.'

# A plain, slightly tapering cover only. Rear details are not observable, so no
# ports, screw holes, ventilation, branding, stand or mounting bracket is invented.
rear = loop_shell('Plain closed rear cover, explicitly inferred', [
    rounded_rectangle(1.532, .882, .008, .450, .004),
    rounded_rectangle(1.532, .882, .008, .450, .020),
    rounded_rectangle(1.496, .846, .015, .450, .035),
], shell_mat, close_ends=True)
rear['evidence'] = 'Hidden rear is a conservative closed tapered envelope, not a product match.'

# The photographed broad top/bottom black areas are video letterboxing, not
# extra physical bezel. A single neutral 16:9 plane replaces all screen content.
screen = loop_shell('Recessed neutral black 16 by 9 screen', [
    rounded_rectangle(1.506, .847125, .0005, .4515625, -.029),
    rounded_rectangle(1.506, .847125, .0005, .4515625, -.025),
], screen_mat, close_ends=True)
screen['evidence'] = 'Display plane visible. Neutral non-emissive material replaces copyrighted moving content.'

root = bpy.data.objects.new(NAME+'_bottom_center', None)
scene.collection.objects.link(root)
root['asset_id'] = NAME
root['version'] = 'v001'
root['unplaced'] = True
root['source_period'] = '2024-09-19 article; current presence unverified'
root['dimensions_estimated_m'] = '1.550 width x 0.070 depth x 0.900 height'
root['front_direction_blender'] = '-Y'
root['hidden_geometry'] = 'Plain inferred rear; mounting hardware intentionally omitted'
for obj in objects:
    obj.parent = root

# Export temporary material batches, preserving the three editable components.
export_objects = []
for mat in [shell_mat, screen_mat]:
    bpy.ops.object.select_all(action='DESELECT')
    copies = []
    for original in objects:
        if original.data.materials[0] == mat:
            cp = original.copy()
            cp.data = original.data.copy()
            cp.parent = None
            scene.collection.objects.link(cp)
            cp.select_set(True)
            copies.append(cp)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    batch = bpy.context.object
    batch.name = 'Monitor_shell' if mat == shell_mat else 'Neutral_screen'
    batch.parent = root
    export_objects.append(batch)
bpy.ops.object.select_all(action='DESELECT')
for obj in export_objects + [root]:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(filepath=str(OUT/(NAME+'.glb')), export_format='GLB',
    use_selection=True, export_yup=True, export_extras=True,
    export_cameras=False, export_lights=False, export_materials='EXPORT')
for obj in export_objects:
    bpy.data.objects.remove(obj, do_unlink=True)
stages['model_exported_utc'] = utc()
stages['geometry_and_export_seconds'] = round(time.perf_counter()-started, 4)

# Studio belongs only to the editable inspection scene, never to the GLB.
world = bpy.data.worlds.new('Neutral inspection studio')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.36, .39, .42, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = .55
target = Vector((0, 0, .45))
for name, loc, power, size in [('Key',(-2.8,-3,3),320,2.2),
                             ('Fill',(3,-1.5,2),190,2.0),
                             ('Rear edge',(1.2,2,2.3),240,2.0)]:
    data = bpy.data.lights.new('STUDIO_ONLY_'+name, 'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new('STUDIO_ONLY_'+name, data)
    scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (target-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data = bpy.data.cameras.new('STUDIO_ONLY_inspection_camera')
cam = bpy.data.objects.new('STUDIO_ONLY_inspection_camera', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
scene.view_settings.view_transform = 'AgX'
render_times = {}
for name, loc, scale in [('front',(0,-4,.45),1.83),
                         ('side',(4,0,.45),1.54),
                         ('oblique',(2.5,-3.5,1.9),1.88)]:
    cam.location = loc
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = scale
    scene.render.filepath = str(OUT/'renders'/(name+'.png'))
    if not SKIP_RENDER:
        t = time.perf_counter()
        start_utc = utc()
        bpy.ops.render.render(write_still=True)
        render_times[name] = {'started_utc':start_utc, 'finished_utc':utc(),
                             'seconds':round(time.perf_counter()-t, 4)}
scene.render.filepath = '//renders/oblique.png'
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = bezel
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'.blend')))
stages['renders'] = render_times
stages['generation_finished_utc'] = utc()
stages['generation_total_seconds'] = round(time.perf_counter()-started, 4)
stages['external_dependencies'] = []
stages['packed_images'] = 0
stages['packed_images_note'] = 'No texture images are needed; all two materials are native standard PBR.'
with open(OUT/'build_stats.json','w') as f:
    json.dump(stages, f, indent=2)
print('BUILD_STATS', json.dumps(stages))
