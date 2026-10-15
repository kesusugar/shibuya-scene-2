import bpy, math, json, sys, os
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[0] if args else Path(__file__).resolve().parents[1]/'output');out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
parts=[]
def mat(n,c,metal=0,rough=.45,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 return m
black=mat('Charcoal powder coated housing',(.018,.021,.024),.1,.6)
metal=mat('Dark swivel metal',(.075,.080,.084),.7,.32)
lens=mat('Warm visible aperture - not a scene light',(.95,.63,.24),0,.3,.35)
def cyl(n,a,b,r,m,verts=32):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);parts.append(o)
 for face in o.data.polygons:face.use_smooth=len(face.vertices)==4
 return o
def box(n,loc,dim,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);parts.append(o)
# Inferred housing: 0.11m diameter, 0.16m body length, tilted down toward -Y.
axis=Vector((0,-.5,-.8660254));back=Vector((0,.025,.16));front=back+axis*.16
housing=cyl('Observed simple cylindrical lamp housing',back,front-axis*.009,.055,black)
# Remove both end ngons: rear cap and recessed aperture are separate surfaces.
import bmesh
bm=bmesh.new();bm.from_mesh(housing.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES');bm.to_mesh(housing.data);bm.free()
cyl('Rear cap',back-axis*.008,back,.052,black)
# Real annular rim rather than an opaque face hiding the lens.
a=front-axis*.009;b=front+axis*.008
u=Vector((1,0,0));v=axis.cross(u).normalized();vs=[]
for p,r in [(a,.055),(b,.055),(b,.044),(a,.044)]:
 for i in range(32):vs.append(tuple(p+r*(u*math.cos(i*math.tau/32)+v*math.sin(i*math.tau/32))))
fs=[]
for ring in range(4):
 for i in range(32):j=(i+1)%32;fs.append((ring*32+i,ring*32+j,((ring+1)%4)*32+j,((ring+1)%4)*32+i))
me=bpy.data.meshes.new('Annular rim');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Open front rim',me);bpy.context.collection.objects.link(o);o.data.materials.append(black);parts.append(o)
for face in me.polygons:face.use_smooth=(face.index//32 in (0,2))
cyl('Recessed warm lens',front-axis*.012,front-axis*.009,.043,lens)
cyl('Swivel axle',(-.065,.005,.14),(.065,.005,.14),.012,metal,16)
box('Short support arm',(.062,.012,.205),(.018,.022,.13),black)
box('Compact mounting foot',(.032,.012,.277),(.10,.055,.014),black)
# Join into one mesh, preserve material slots; origin at bounding-box bottom centre.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;obj.name='shibu_hachi_box_display_spotlight'
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
coords=[obj.matrix_world@v.co for v in obj.data.vertices];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for vert in obj.data.vertices:vert.co=obj.matrix_world@vert.co-offset
obj.matrix_world.identity();scene.cursor.location=(0,0,0)
obj['reference_date']='2026-08-08';obj['dimensions_status']='Estimated from photograph; not measured';obj['placement_status']='Unplaced. Codex owns integration.'
obj.data.calc_loop_triangles();mount=Vector((.032,.012,.284))-offset
meta={'name':obj.name,'units':'meters','origin':'bottom centre of full fixture bounds','dimensions_m':list(hi-lo),'triangles':len(obj.data.loop_triangles),'materials':len(obj.data.materials),'mount_datum_blender_m':list(mount),'forward_blender':[0,-1,0],'up_blender':[0,0,1],'runtime_lights':False,'date':'2026-08-08','geometry_estimated':True}
(out/'asset.json').write_text(json.dumps(meta,indent=2))
bpy.ops.export_scene.gltf(filepath=str(out/(obj.name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
# Save portable authoring model without context geometry, file images, or real-time lamps.
bpy.ops.wm.save_as_mainfile(filepath=str(out/(obj.name+'.blend')))
if '--no-render' in args:sys.exit(0)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world.color=(.25,.25,.25);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((1,-1,2),90,2),((-1,-.3,.8),45,1),((0,1,1.4),70,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,.15))
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.42
for name,loc in [('front',(0,-1,.20)),('side',(1,0,.20)),('oblique',(.7,-1,.10))]:
 cam.location=loc;aim(cam,(0,0,.145));scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('ASSET_REPORT '+json.dumps(meta))
