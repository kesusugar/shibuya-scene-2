import bpy,os,json,collections
from mathutils import Vector
D=os.path.dirname(os.path.abspath(__file__))
r=json.load(open(os.path.join(D,'batch_identity.json')))
# Use original lighting and camera, but replace authoring meshes by actual GLB import.
bpy.ops.wm.open_mainfile(filepath=os.path.join(D,'shibuhachibox_counter.blend'))
for ob in list(bpy.context.scene.objects):
 if ob.type in ('MESH','EMPTY'):bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(D,'shibuhachibox_counter.glb'))
s=bpy.context.scene;s.render.filepath=os.path.join(D,'glb_reimport.png');bpy.ops.render.render(write_still=True)
# Correct side preview margin, now using GLB geometry.
c=s.camera;c.location=(4,0,.6);c.rotation_euler=(Vector((0,0,.49))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=1.8;s.render.filepath=os.path.join(D,'side.png');bpy.ops.render.render(write_still=True)
print('BATCH_IDENTITY',r)
