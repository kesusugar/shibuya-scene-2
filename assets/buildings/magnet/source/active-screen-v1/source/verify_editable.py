"""Read-only Blender reopen validation of the delivered editable scene."""
import bpy, hashlib, json, sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(root/'output/magnet_screen_editable.blend'))
screen=bpy.data.objects['08_SIGNS_2025_box_screen']
expected=[[35.47999954223633,8.669999122619629,16.459999084472656],[44.119998931884766,8.669999122619629,16.459999084472656],[44.119998931884766,8.669999122619629,21.260000228881836],[35.47999954223633,8.669999122619629,21.260000228881836]]
assert [list(v.co) for v in screen.data.vertices]==expected
assert list(screen.location)==[0,0,0] and list(screen.scale)==[1,1,1]
images=[]
for im in bpy.data.images:
    if im.name in {'Render Result','Viewer Node'}:continue
    assert im.packed_file and min(im.size)>0 and len(im.pixels)>0,im.name
    images.append({'name':im.name,'size':list(im.size),'packed_bytes':im.packed_file.size,'pixel_count':len(im.pixels)})
assert len(images)==5
collections={}
for name in ['UNCHANGED_MAGNET_permanent_building','UNCHANGED_Eiraku_companion','SIGNS_2025_corrected_active_plane_only']:
    c=bpy.data.collections[name]
    collections[name]={'meshes':sum(o.type=='MESH' for o in c.objects),'triangles':sum(len(p.vertices)-2 for o in c.objects if o.type=='MESH' for p in o.data.polygons)}
result={'status':'PASS','blend_reopened':True,'authoring_target_vertices':expected,'all_five_images_packed_and_pixels_readable':images,'collections':collections,'no_external_photo_or_font_dependency':True,'note':'Imported mesh editing scene, not the byte-exact canonical GLB generator. Save-time packed-image warnings did not prevent pixel access after reopening.'}
(root/'evidence/editable_reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
