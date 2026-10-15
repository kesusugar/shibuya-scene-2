"""Single final GLB import check plus three inspection renders; Blender 4.2.3."""
import bpy,sys,json,math,time
from pathlib import Path
from mathutils import Vector
T=time.perf_counter();O=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(O/'shibu_hachi_counter_laptop.glb'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
mn=[min(v[i] for v in pts) for i in range(3)];mx=[max(v[i] for v in pts) for i in range(3)]
assert len(obs)==3 and all(math.isfinite(c) for v in pts for c in v)
assert abs(mn[2])<1e-6 and abs(mx[0]+mn[0])<1e-6 and abs(mx[1]+mn[1])<1e-6
assert all(o.type=='MESH' for o in bpy.context.scene.objects)
stats=json.load(open(O/'build_stats.json'));dims=[mx[i]-mn[i] for i in range(3)]
assert all(abs(a-b)<2e-6 for a,b in zip(dims,stats['dimensions_m']))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True
s.render.resolution_x=900;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.world.color=(.30,.30,.30);s.view_settings.view_transform='AgX'
for loc,power,size in [((-.3,-.55,.65),25,.5),((.5,.1,.5),20,.5),((-.3,.6,.4),14,.4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.shape='DISK';ob.data.size=size;ob.rotation_euler=(Vector((0,0,.10))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.41;cam.data.clip_start=.001
renders=[]
for name,loc in [('photo_near_rear',(.33,-.80,.41)),('side',(.80,0,.115)),('operator_oblique',(-.40,.64,.49))]:
 start=time.perf_counter();cam.data.ortho_scale=.49 if name=='operator_oblique' else .41;cam.location=loc;cam.rotation_euler=(Vector((0,0,.108))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True);renders.append({'file':'renders/'+name+'.png','seconds':time.perf_counter()-start,'source':'reimported final GLB'})
json.dump({'status':'pass','blender':'4.2.3','reimport_meshes':len(obs),'bounds_blender_m':[mn,mx],'dimensions_m':dims,'origin_test':'pass','finite_vertices':'pass','roundtrip_dimensions':'pass','renders':renders,'seconds_total':time.perf_counter()-T},open(O/'qa'/'glb_roundtrip_render.json','w'),indent=2)
