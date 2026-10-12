# Clay render of the MAGNET PLATEAU LOD2 surfaces, for reading the massing and for the camera fit.
#   blender -b -P lod2_clay.py -- <lod2.json> <out.png> <camX> <camY> <camZ> <tgtX> <tgtY> <tgtZ> <lens_mm> [W H]
import bpy, json, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
d = json.load(open(a[0])); out = a[1]
cam = Vector(map(float, a[2:5])); tgt = Vector(map(float, a[5:8])); lens = float(a[8])
W, H = (int(a[9]), int(a[10])) if len(a) > 10 else (1280, 960)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
cols = {'GroundSurface': (.3, .5, .3, 1), 'RoofSurface': (.85, .35, .3, 1), 'WallSurface': (.8, .8, .78, 1)}
for k, c in cols.items():
    m = bpy.data.materials.new(k); m.diffuse_color = c; m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = c
    verts, faces = [], []
    for s in d[k]:
        i0 = len(verts); verts += [tuple(p) for p in s[:-1] if True]; faces.append(list(range(i0, len(verts))))
    me = bpy.data.meshes.new(k); me.from_pydata(verts, [], faces); me.materials.append(m)
    ob = bpy.data.objects.new(k, me); sc.collection.objects.link(ob)
# ground plane + axes markers (1 m posts every 10 m along X and Y)
bpy.ops.mesh.primitive_plane_add(size=400, location=(30, 30, -0.02))
for x in range(0, 80, 10):
    bpy.ops.mesh.primitive_cube_add(size=.6, location=(x, 0, .3))
cd = bpy.data.cameras.new('c'); cd.lens = lens; cd.sensor_width = 36
co = bpy.data.objects.new('c', cd); sc.collection.objects.link(co); co.location = cam
co.rotation_euler = (tgt - cam).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sun = bpy.data.lights.new('s', 'SUN'); sun.energy = 3; so = bpy.data.objects.new('s', sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(30))
sc.world = bpy.data.worlds.new('w'); sc.world.color = (.6, .7, .9)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.use_denoising = False; sc.cycles.device = 'CPU'
sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.6, .7, .9, 1); sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.filepath = out
bpy.ops.render.render(write_still=True)
