"""Blender 4.2.3: editable imported meshes + packed baseline art; no GLB re-export.
Example: blender -b -t 4 --python-exit-code 1 -P source/build_editable.py -- --root . --render
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--render',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=args.root.resolve(); inputs=root/'inputs'; output=root/'output'; evidence=root/'evidence'
output.mkdir(parents=True,exist_ok=True);evidence.mkdir(parents=True,exist_ok=True)
assert bpy.app.version[:3]==(4,2,3),bpy.app.version_string
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
provenance={'blender_version':bpy.app.version_string,'coordinate_space':'Inherited authoring X east / Y north / Z up, metres. No rebasing.','render_scope':'Asset-only diagnostic renders, not a walking or FPS test. Cameras retained from the accepted generator. Not a photo-camera calibration.','inputs':{},'cameras':{},'renders':[]}

def import_collection(name,path):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path),import_pack_images=True)
    objs=sorted(set(bpy.data.objects)-before,key=lambda o:o.name)
    collection=bpy.data.collections.new(name);scene.collection.children.link(collection)
    for o in objs:
        for c in list(o.users_collection):c.objects.unlink(o)
        collection.objects.link(o)
    provenance['inputs'][name]={'filename':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':len(objs),'meshes':sum(o.type=='MESH' for o in objs),'triangles':sum(len(p.vertices)-2 for o in objs if o.type=='MESH' for p in o.data.polygons)}
    return collection,objs

base,base_objects=import_collection('UNCHANGED_MAGNET_permanent_building',inputs/'magnet.unchanged.glb')
neighbor,neighbor_objects=import_collection('UNCHANGED_Eiraku_companion',inputs/'eiraku.unchanged.glb')
signs,sign_objects=import_collection('SIGNS_2025_corrected_active_plane_only',output/'magnet_signs_2025.glb')
screen=next(o for o in sign_objects if o.name=='08_SIGNS_2025_box_screen')
assert screen.type=='MESH' and len(screen.data.vertices)==4
new_vertices=[v.co.copy() for v in screen.data.vertices]
# Record and reconstruct old positions by corner, not by exporter-dependent vertex order.
sys.path.insert(0,str(root/'source'))
from correct_screen import read_glb, values
_,_,bj,bb=read_glb(inputs/'magnet_signs_2025.before.glb')
bn=next(n for n in bj['nodes'] if n.get('name')=='08_SIGNS_2025_box_screen')
bp=bj['meshes'][bn['mesh']]['primitives'][0]
old_vertices=[Vector((v[0],-v[2],v[1])) for v in values(bj,bb,bp['attributes']['POSITION'])]

camera_collection=bpy.data.collections.new('DIAGNOSTIC_CAMERAS_existing_authoring_views');scene.collection.children.link(camera_collection)
def camera(name,pos,target,lens,res):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);camera_collection.objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.1;data.clip_end=3000
    provenance['cameras'][name]={'position':list(pos),'target':list(target),'lens_mm':lens,'resolution':list(res),'basis':'Unchanged camera_look south view from accepted build_magnet.py'}
    return o,res
south=camera('existing_south_view',(40,-55,4),(40,15,22),30,(1100,1400))
fit=json.loads((inputs/'camera_m027_fit.json').read_text())
data=bpy.data.cameras.new('existing_m027_view');m027=bpy.data.objects.new('existing_m027_view',data);camera_collection.objects.link(m027)
y,p,r=map(math.radians,(fit['yaw'],fit['pitch'],fit['roll']))
f=Vector((math.sin(y)*math.cos(p),math.cos(y)*math.cos(p),math.sin(p)))
rt=Vector((math.cos(y),-math.sin(y),0));up=rt.cross(f)
rt2=rt*math.cos(r)-up*math.sin(r);up2=up*math.cos(r)+rt*math.sin(r)
m027.matrix_world=Matrix((rt2,up2,-f)).transposed().to_4x4();m027.location=fit['pos']
data.sensor_fit='HORIZONTAL';data.angle_x=2*math.atan(fit['W']/2/fit['fpx']);data.clip_end=3000
provenance['cameras']['existing_m027_view']={'fit':fit,'resolution':[fit['W'],fit['H']],'basis':'Unchanged inherited camera; no source photo loaded or redistributed.'}

scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24
scene.cycles.use_denoising=True;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
scene.cycles.max_bounces=6;scene.cycles.transparent_max_bounces=12
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=94;scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
world=bpy.data.worlds.new('Diagnostic illumination, no photo or HDRI');world.use_nodes=True;scene.world=world
bg=world.node_tree.nodes['Background']
light_data=bpy.data.lights.new('Inspection sun','SUN');light_data.angle=math.radians(.6)
light=bpy.data.objects.new('Inspection sun',light_data);scene.collection.objects.link(light)
az,el=map(math.radians,(207,57));direction=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
light.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()

def apply_time(mode):
    table=json.loads((inputs/f'emissive_{mode}.json').read_text())
    for material in bpy.data.materials:
        row=table.get(material.name)
        if row and material.use_nodes:
            for n in material.node_tree.nodes:
                if n.type=='BSDF_PRINCIPLED':
                    n.inputs['Emission Strength'].default_value=row['estr']
    bg.inputs['Color'].default_value=(.38,.50,.68,1) if mode=='day' else (.004,.006,.02,1)
    bg.inputs['Strength'].default_value=.65 if mode=='day' else .25
    light_data.energy=3 if mode=='day' else .08

def state(which):
    for v,p in zip(screen.data.vertices,new_vertices if which=='after' else old_vertices):v.co=p
    screen.data.update();bpy.context.view_layer.update()

def render(name,which,time,cam,res):
    state(which);apply_time(time);scene.camera=cam
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(evidence/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
    provenance['renders'].append({'file':name+'.jpg','state':which,'time':time,'camera':cam.name,'resolution':list(res),'sha256':hashlib.sha256((evidence/(name+'.jpg')).read_bytes()).hexdigest()})

if args.render:
    render('south_day_before','before','day',*south)
    render('south_day_after','after','day',*south)
    # render('south_night_before','before','night',*south)
    # render('south_night_after','after','night',*south)
    # render('m027_day_before','before','day',m027,(fit['W'],fit['H']))
    # render('m027_day_after','after','day',m027,(fit['W'],fit['H']))

state('after');apply_time('day');scene.camera=south[0]
scene.render.resolution_x,scene.render.resolution_y=south[1]
scene.render.filepath='//../evidence/south_day_after.png'
for im in bpy.data.images:
    if im.name not in {'Render Result','Viewer Node'}:
        if not im.packed_file:im.pack()
        im.filepath='//packed/'+im.name
scene['scope']='Only the active screen quad was corrected; the other imported mesh geometry and source GLB data are unchanged. This .blend is an editable derived scene, not the canonical byte-preserving exporter.'
scene['canonical_generator']='../source/correct_screen.py with ../inputs/'
scene['runtime_placement']='Authoring coordinates retained. Existing viewer offset is -0.093 m; apply once in runtime, not to these vertices.'
scene['photo_rights']='No HUIS photo pixels or campaign graphics included. Existing original placeholder preserved.'
scene['geometry_uncertainty']='Active dimensions authoritative; centre photo-informed. Inherited cassette is uncalibrated: ~0.69 m conflict at each photo-mapped edge; manual-pick centre sensitivity 18.72-19.00 m.'
bpy.ops.object.select_all(action='DESELECT');screen.select_set(True);bpy.context.view_layer.objects.active=screen
bpy.ops.wm.save_as_mainfile(filepath=str(output/'magnet_screen_editable.blend'),relative_remap=False)
provenance['editable_blend']={'file':'magnet_screen_editable.blend','sha256':hashlib.sha256((output/'magnet_screen_editable.blend').read_bytes()).hexdigest(),'packed_images':[im.name for im in bpy.data.images if im.packed_file],'authoring_screen_vertices':[list(v.co) for v in screen.data.vertices]}
(evidence/'render_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('EDITABLE_AND_RENDERS_OK',provenance['editable_blend'])
