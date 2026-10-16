"""Independent visible cladding only. Blender 4.2.3. No photo textures.
Run: blender --background --factory-startup --python this.py -- --out DIRECTORY
Optional --no-render is for the one clean regeneration check.
"""
import argparse, bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1]); p.add_argument('--no-render', action='store_true'); args = p.parse_args(argv)
out=args.out.resolve(); name='jr_miyamasuzaka_visible_centre_pier_20250409_v001'
for child in ('model','evidence','validation'): (out/child).mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
W,H,D=2.2,4.2,0.20; BW,BH=0.17,2.73; Y=-D/2

def lin(v): return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4

def material(name,hexstr):
    rgb=tuple(lin(int(hexstr[i:i+2],16)/255) for i in (0,2,4))
    mat=bpy.data.materials.new(name); mat.diffuse_color=(*rgb,1); mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF'); shader.inputs['Base Color'].default_value=(*rgb,1); shader.inputs['Roughness'].default_value=.85
    mat.use_backface_culling=False
    return mat
pale=material('cladding_pale_approximate','deded6'); green=material('edge_protection_mint_approximate','66c6aa'); white=material('edge_protection_white_approximate','ecede7')
vertices=[]; faces=[]; indices=[]
def face(coords,mat_index):
    clean=[]
    for v in coords:
        if not clean or sum((a-b)**2 for a,b in zip(v,clean[-1]))>1e-18: clean.append(v)
    if len(clean)>1 and sum((a-b)**2 for a,b in zip(clean[0],clean[-1]))<1e-18: clean.pop()
    if len(clean)<3: return
    start=len(vertices); vertices.extend(clean); faces.append(tuple(range(start,start+len(clean)))); indices.append(mat_index)
def front_rect(x0,x1,z0,z1,mat_index=0): face([(x0,Y,z0),(x1,Y,z0),(x1,Y,z1),(x0,Y,z1)],mat_index)
# Three front regions leave exact space for the lower edge-protection inlays.
front_rect(-W/2+BW,W/2-BW,0,BH); front_rect(-W/2,W/2,BH,H)
# The visible right return is a technical 0.20 m shallow surface, not a pier core.
face([(W/2,-D/2,0),(W/2,D/2,0),(W/2,D/2,H),(W/2,-D/2,H)],0)

def clip(poly,fn):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        fa,fb=fn(a),fn(b); ina,inb=fa>=-1e-10,fb>=-1e-10
        if ina: result.append(a)
        if ina != inb:
            t=fa/(fa-fb); result.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    return result
# Alternating bands are independent geometry/materials, not image-derived textures.
# Their pitch and slope are visual estimates; individual scratches/peeling are omitted.
for x0 in (-W/2,W/2-BW):
    rect=[(x0,0),(x0+BW,0),(x0+BW,BH),(x0,BH)]
    pitch=.19; slope=.65
    for k in range(-2,18):
        low=k*pitch; high=(k+1)*pitch
        poly=clip(rect,lambda q:q[1]-slope*(q[0]-x0)-low)
        poly=clip(poly,lambda q:high-(q[1]-slope*(q[0]-x0))) if poly else []
        if len(poly)>=3: face([(x,Y,z) for x,z in poly],1 if k%2==0 else 2)
mesh=bpy.data.meshes.new('visible_L_shell_surfaces'); mesh.from_pydata(vertices,[],faces); mesh.materials.clear()
for mat in (pale,green,white): mesh.materials.append(mat)
for poly,idx in zip(mesh.polygons,indices): poly.material_index=idx
mesh.update(); obj=bpy.data.objects.new('visible_centre_pier_cladding_ONLY',mesh); scene.collection.objects.link(obj)
obj['scope']='Front cladding and shallow right return only; open surface shell, no hidden structure.'
obj['reference_capture_date']='2025-04-09'; obj['dimensions_status']='Unmeasured rounded nominal estimates; not fit-ready.'
obj['nominal_width_height_depth_m']=[W,H,D]; obj['source_url']='https://biz.shibuyabunka.com/watch/50/'
# Triangulation explicitly fixes topology for reliable glTF regeneration.
bpy.context.view_layer.objects.active=obj; obj.select_set(True)
tri=obj.modifiers.new('Explicit_triangulation','TRIANGULATE'); bpy.ops.object.modifier_apply(modifier=tri.name)
bpy.ops.export_scene.gltf(filepath=str(out/'model'/f'{name}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False)
# Studio is preview-only, excluded from the exported GLB.
asset_collection=bpy.data.collections.new('ASSET_export_only_this_collection'); scene.collection.children.link(asset_collection)
for col in list(obj.users_collection): col.objects.unlink(obj)
asset_collection.objects.link(obj)
studio=bpy.data.collections.new('STUDIO_preview_only_NOT_ASSET'); scene.collection.children.link(studio)
def into_studio(o):
    for col in list(o.users_collection): col.objects.unlink(o)
    studio.objects.link(o)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.012)); ground=bpy.context.object; ground.name='preview_ground_NOT_ASSET'; into_studio(ground); ground.data.materials.append(material('studio_neutral','92979b'))
world=bpy.data.worlds.new('studio_world') if not scene.world else scene.world; scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.69,.75,1); world.node_tree.nodes['Background'].inputs[1].default_value=.6
for label,loc,power,size in [('key',(-3,-5,7),900,5),('fill',(4,-2,5),400,4)]:
    data=bpy.data.lights.new(label,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; light=bpy.data.objects.new(label,data); studio.objects.link(light); light.location=loc; light.rotation_euler=(Vector((0,0,2))-light.location).to_track_quat('-Z','Y').to_euler()
camera_data=bpy.data.cameras.new('front_oblique_preview'); camera=bpy.data.objects.new('front_oblique_preview',camera_data); studio.objects.link(camera); camera.location=(5,-9,5.25); camera.rotation_euler=(Vector((0,0,2.0))-camera.location).to_track_quat('-Z','Y').to_euler(); camera_data.type='ORTHO'; camera_data.ortho_scale=5.55; scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=32; scene.cycles.use_denoising=True
scene.render.resolution_x=1000; scene.render.resolution_y=1100; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(out/'evidence'/'front_oblique.png')
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.wm.save_as_mainfile(filepath=str(out/'model'/f'{name}.blend'))
if not args.no_render: bpy.ops.render.render(write_still=True)
info={'blender_version':bpy.app.version_string,'asset':name,'asset_objects':1,'triangles':len(obj.data.polygons),'materials':3,'textures':0,'blender_bounds_m':[[-W/2,-D/2,0],[W/2,D/2,H]],'nominal_width_height_depth_m':[W,H,D],'origin':'bottom-centre (0,0,0)','blender_front':'-Y','gltf_front':'+Z','geometry':'Open front + right return surface shell; double-sided materials; intentionally not watertight','rendered':not args.no_render}
(out/'validation'/'build_stats.json').write_text(json.dumps(info,indent=2)+'\n')
print('BUILD_COMPLETE',json.dumps(info))
