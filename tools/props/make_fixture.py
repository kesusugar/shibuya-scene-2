"""Self-test fixture for import_prop.py: a deliberately messy 'vending machine' (centimetre scale, offset from the
origin, three separate objects, one triangle-heavy part). blender -b -P make_fixture.py -- out.glb"""
import bpy, sys
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(n, c):
    m = bpy.data.materials.new(n); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*c, 1); return m
bpy.ops.mesh.primitive_cube_add(location=(500, 300, 91.5)); b = bpy.context.object; b.scale = (50, 37.5, 91.5); b.data.materials.append(mat('Body_Red', (.7, .05, .05)))
bpy.ops.mesh.primitive_cube_add(location=(500, 262, 120)); g = bpy.context.object; g.scale = (40, 1, 45); g.data.materials.append(mat('Front_Glass', (.2, .3, .35)))
bpy.ops.mesh.primitive_uv_sphere_add(location=(500, 262, 40), segments=128, ring_count=64, radius=8); s = bpy.context.object; s.data.materials.append(mat('Button_Metal', (.6, .6, .6)))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True)
