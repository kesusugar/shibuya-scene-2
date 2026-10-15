"""Blender 4.2.3: import exact delivered GLBs; save editable scene and paired views."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];assert bpy.app.version==(4,2,3),bpy.app.version_string
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'output/center244.glb'))
bpy.ops.import_scene.gltf(filepath=str(R/'inputs/signs-2025-01.glb'))
q=json.loads((R/'inputs/PROPOSAL.json').read_text());a=Vector(q['origin_a']);t=Vector(q['tangent']);n=Vector(q['outward']);W=q['face_width_m'];aim=a+t*W*.52+Vector((0,0,4.1))
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='diagnostic_camera';cam.data.type='ORTHO';bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='SUN',location=(-50,30,70));light=bpy.context.object;light.rotation_euler=(aim-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=2
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.world=bpy.data.worlds.new('World');s.world.color=(.5,.5,.5);s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
new=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('c244_chamfer_cassette')];assert len(new)==1
new[0]['evidence']='2022 detailed + undated shape; February 2025 partial persistence; October inferred'
new[0]['scope']='top housing, two squared end caps, recessed slot; no fabric or hardware'
camdata={}
for label,center,offset,scale in [('overview',aim,n*16+Vector((0,0,3)),6.4),('front',a+t*W*.52+Vector((0,0,4.56)),n*16+Vector((0,0,.9)),3.6),('side',a+t*W*.52+Vector((0,0,4.56)),n*10+t*10+Vector((0,0,3)),3.6)]:
 cam.location=center+offset;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;camdata[label]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':scale}
 for state in ['before','after']:
  new[0].hide_render=state=='before';s.render.filepath=str(R/'evidence'/f'{label}-{state}.png');bpy.ops.render.render(write_still=True)
new[0].hide_render=False
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
s['coordinate_convention']='Blender X east Y north Z TP-15; glTF=(X,Z,-Y); viewer groundElevationTP 15 unchanged'
s['not_surveyed']=True;bpy.ops.wm.save_as_mainfile(filepath=str(R/'output/center244-cassette.blend'))
(R/'evidence/cameras.json').write_text(json.dumps(camdata,indent=2)+'\n')
(R/'evidence/blender.json').write_text(json.dumps({'version':bpy.app.version_string,'new_object':new[0].name,'triangles':sum(len(p.vertices)-2 for p in new[0].data.polygons),'materials':len(new[0].data.materials),'image_paths_packed':all(i.packed_file is not None for i in bpy.data.images if i.source=='FILE' and i.has_data)},indent=2)+'\n')
