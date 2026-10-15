"""Identical-camera before/after Workbench evidence and packed editable Blender 4.2.3 file."""
import bpy, json
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parents[2]; E=A/'evidence/cumulative-v2/lower'; E.mkdir(parents=True,exist_ok=True)
assert bpy.app.version==(4,2,3), 'Use Blender 4.2.3 for this evidence'
origin=Vector((255.985,-290.160,0)); end=Vector((279.103,-264.434,0)); tangent=(end-origin).normalized(); outward=Vector((tangent.y,-tangent.x,0))
focus=origin+(end-origin)*.275+Vector((0,0,83.022)); seam=origin+(end-origin)*.275+Vector((0,0,90.804))
views=[('southeast',(610,-840,155),(237,-255,95),215,(850,1300)),
       ('southwest',(60,-850,155),(237,-255,95),215,(850,1300)),
       ('lower-field',tuple(focus+outward*100),tuple(focus),23,(1100,1100)),
       ('upper-seam',tuple(seam+outward*100),tuple(seam),13,(1400,850))]
settings=[]
for stage,source in [('before',A/'source/data/panel-baseline/stream.glb'),('after',A/'web/stream.glb')]:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=str(source))
    s=bpy.context.scene; s.render.engine='BLENDER_WORKBENCH'; s.display.shading.light='STUDIO'; s.display.shading.studiolight_rotate_z=0.45; s.display.shading.color_type='MATERIAL'
    s.world=bpy.data.worlds.new('Review'); s.world.color=(.15,.17,.2); s.view_settings.view_transform='Standard'; s.view_settings.exposure=0.8; s.render.resolution_percentage=100; s.render.image_settings.file_format='JPEG'; s.render.image_settings.quality=92
    for name,location,target,scale,resolution in views:
        bpy.ops.object.camera_add(); cam=bpy.context.object; cam.name='Review_'+name; s.camera=cam; cam.data.type='ORTHO'
        cam.location=location; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
        s.render.resolution_x,s.render.resolution_y=resolution; s.render.filepath=str(E/f'{stage}-{name}.jpg'); bpy.ops.render.render(write_still=True)
        if stage=='after':settings.append({'view':name,'location':location,'target':target,'ortho_scale':scale,'resolution':resolution})
# Scene currently contains after geometry only. Pack every provided image; use relative filepaths.
s.render.filepath='//review.jpg'; s.render.film_transparent=False
embedded=['build.py','test.py','test-panel-rhythm.py','render.py','verify_blend.py','lower-panel-trace.json','build-report.json','LOWER-PANEL-SOURCE.md']
for name in embedded:
    path=A/'source/blender'/name if name.endswith('.py') else A/'source/data'/name if name.endswith('.json') else A/'source/refs'/name
    text=bpy.data.texts.new(name); text.write(path.read_text())
for name in ['reference-CC0.jpg','DEC01-lower112-left-unmarked.jpg','DEC01-lower112-six-rectangles.jpg']:
    ref=bpy.data.images.load(str(A/'source/refs'/name)); ref.use_fake_user=True; ref.pack(); ref.filepath='//../refs/'+name
bpy.ops.file.pack_all()
# Relative paths must also cover packed-file records and editor bookmarks.
for image in bpy.data.images:
    if image.source=='FILE':
        image.filepath='//../refs/'+image.name
        for packed in image.packed_files: packed.filepath=image.filepath
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params: space.params.directory=b'//'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(A/'source/blender/stream.blend'))
(E/'cameras.json').write_text(json.dumps({'same_camera_for_before_and_after':True,'photograph_camera_calibrated':False,'renderer':'Blender 4.2.3 Workbench studio material colors; actual main versus final','views':settings},indent=2)+'\n')
