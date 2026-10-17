"""Inspect all visible surface intersections at the rear tree trunk centre."""
import bpy
import sys
from mathutils import Vector

paths = sys.argv[sys.argv.index('--') + 1:]
point = Vector((7.4, -45.5, 30))
for path in paths:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    hits = []
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        local_start = ob.matrix_world.inverted() @ point
        local_direction = (ob.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized()
        result = ob.ray_cast(local_start, local_direction)
        if result[0]:
            world = ob.matrix_world @ result[1]
            hits.append((ob.name, round(world.z, 5)))
    print(path, sorted(hits, key=lambda x: -x[1]))
