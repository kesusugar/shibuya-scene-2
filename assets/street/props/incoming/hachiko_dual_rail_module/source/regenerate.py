"""Blender 4.2.3: standalone partial dual-tube rail. No ground or runtime edits.
Usage: blender -b -P regenerate.py -- OUTPUT [--baseline]
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]).resolve();out.mkdir(parents=True,exist_ok=True);old='--baseline' in args
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
mat=bpy.data.materials.new('rail_silver');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.55,.58,.60,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.32
parts=[]
def finish(o,name):
 o.name=name;o.data.materials.append(mat);parts.append(o);return o
def tube(name,p,q,r,n=20):
 p,q=Vector(p),Vector(q);bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(q-p).length,location=(p+q)/2);o=bpy.context.object;o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler()
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return finish(o,name)
def blade(name,x,points,thickness):
 verts=[(x+dx,y,z) for dx in [-thickness/2,thickness/2] for y,z in points];n=len(points);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name)
# Length and tube elevations preserved from accepted generator; not measured.
for y,z in [(.11,.65),(-.11,.81)]:tube('longitudinal_tube',(-1.125,y,z),(1.125,y,z),.035)
if old:
 for i in range(4):
  x=-1.095+i*2.19/3;tube('old_round_brace',(x,.11,.65),(x,-.11,.81),.014,12);tube('old_round_leg',(x,.01,.01),(x,.01,.65),.018,12)
else:
 # Visible flat end cheeks, continuing into flat front legs; concealed anchorage omitted.
 # Side silhouette is continuous, unlike disconnected legacy round legs.
 profile=[(.085,0),(.13,0),(.13,.65),(-.082,.845),(-.133,.825),(.085,.625)]
 for x in [-1.125,1.125]:blade('flat_end_cheek_and_leg',x,profile,.012)
 # A narrow intermediate flat cross-strap is visible in July095. Its hidden mate is inferred.
 for x in [-.365,.365]:blade('intermediate_flat_strap',x,[(.12,.63),(.13,.655),(-.102,.825),(-.12,.802)],.010)
# Bake one mesh, preserving local bottom-centre origin. No packed files or photo textures.
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='hachiko_dual_rail_module';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Normalize plan-bound centre (profile rear extent is asymmetric) without changing relative shape.
vs=[v.co for v in o.data.vertices];yc=(min(v.y for v in vs)+max(v.y for v in vs))/2
for v in o.data.vertices:v.co.y-=yc
bpy.ops.export_scene.gltf(filepath=str(out/'hachiko_dual_rail_module.glb'),export_format='GLB',export_yup=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hachiko_dual_rail_module.blend'),compress=True)
vs=[v.co for v in o.data.vertices]
s={'blender':bpy.app.version_string,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons),'materials':1,'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'origin':'plan bounds centre, bottom Z=0','units':'metres','old':old,'y_recentering_m':yc,'placement_y_offset_from_stone_module_m':.12+yc,'scope':'one partial straight rail run; no complete footprint, wall, foliage or runtime placement','estimates':'all metric dimensions; symmetry and intermediate strap positions inferred; concealed fixings omitted'}
(out/'model_stats.json').write_text(json.dumps(s,indent=2)+'\n')
