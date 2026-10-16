"""BOX-1 only: retained architectural shell + one terrace, rigid world placement.
Blender 4.2.3: blender -b --python-exit-code 1 -t 4 -P this_file
Inputs in the repository are immutable; no comparison assembly is imported.
"""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[1]
REPO = R.parents[2]
assert bpy.app.version == (4, 2, 3)
shell = REPO/'assets/street/props/incoming/shibu_hachi_box_architecture_reference/output/shibu_hachi_box.blend'
terrace = R/'source/terrace-v001/shibu_hachi_front_terrace_candidate_v001.glb'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(shell) == '54e6add82ba35918f01496ab1a4402bdf6ad994edf1e7d26f893f8afb1528ec2'
assert sha(terrace) == '6198b2ee3c7d9ce114c9d738f80d72d42aac32610437c715cedd4b7bcfd554df'
position_source = json.loads((REPO/'evidence/box-1/box-position-source.json').read_text(encoding='utf-8'))
ring = [Vector((*p, 0)) for p in position_source['ring_plan_m'][:4]]
centre = sum(ring, Vector())/4
axis = (ring[1]-ring[0]).normalized()
yaw = math.atan2(axis.y, axis.x)
rotation = Matrix.Rotation(yaw, 4, 'Z')
# Use the OSM plaza-facing long edge as the estimated FRONT WALL datum.
# The OSM polygon is ~3.13m deep vs 2.244m wall-centre depth. A centre fit
# intersected the independently baked A8 frontage; do not stretch either asset.
front_mid=(ring[0]+ring[1])/2
origin = front_mid - rotation @ Vector((0, -.536, 0))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(REPO/'assets/ground/core/web/ground_core.glb'))
bm = bmesh.new()
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH' and o.name.startswith(('ground_sidewalk', 'ground_road', 'ground_intersection', 'ground_fill')):
        me=o.data.copy(); me.transform(o.matrix_world); bm.from_mesh(me); bpy.data.meshes.remove(me)
bvh=BVHTree.FromBMesh(bm); bm.free()
def ground(x,y):
    hit=bvh.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    assert hit is not None, 'Missing ground is not zero'
    return hit.z
samples=[]
for x in [-6.2795,-4,-2,0,2,4,6.2795]:
    for y in [-1.786,-.68,1.786]:
        p=origin+rotation@Vector((x,y,0))
        samples.append({'local':[x,y], 'xy':[p.x,p.y], 'ground_y':ground(p.x,p.y)})
# Measure actual pavement; neither the shell base nor terrace AABB is ground.
terminal=origin+rotation@Vector((5.744397750235235,-1.786,0))
terminal_ground=ground(terminal.x,terminal.y)
# R3 is the delivered visible boundary, not a claim about the real ramp terminal.
# Its top is raw Z=-.081863014; do not bury the sloping walking surface.
anchor=terminal_ground+.081863014+.005
origin.z=anchor
world=Matrix.Translation(origin)@rotation

bpy.ops.wm.open_mainfile(filepath=str(shell))
originals=[o for o in bpy.context.scene.objects if o.type=='MESH']
protected={n: [list(o.matrix_world@v.co) for v in o.data.vertices] for n in ['Platform_main_inferred_slab','Rear_closure_INFERRED'] for o in originals if o.name==n}
assert len(protected)==2, 'Editable named architectural components required'
removed=[]
for o in list(originals):
    if o.name.startswith(('Front_rail_', 'Unbranded_front_rail_glass','Base_panel_joint','Front_dark_base_trim','Identifier_carrier_estimated','SHIBU_HACHI_BOX_factual_identifier')):
        removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
# Exact footprint from prior bounded fit; apply only to five named old slab/step objects.
x0,x1=-5.953958414148326,5.744397750235235
bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(-1.786-.886)/2,0))
cutter=bpy.context.object; cutter.name='TEMP_FRONT_REPLACEMENT_PRISM';cutter.dimensions=(x1-x0,.90004,8)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
cut=[]
for o in list(bpy.context.scene.objects):
    if o.name.startswith(('Front_platform_central','End_approach_low_step_','End_threshold_step_')):
        before=len(o.data.polygons)
        mod=o.modifiers.new('BOX1 front footprint only','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        cut.append({'name':o.name,'polygons_before':before,'polygons_after':len(o.data.polygons)})
assert len(cut)==5
bpy.data.objects.remove(cutter,do_unlink=True)
for name,coords in protected.items():
    o=bpy.data.objects[name];assert coords==[list(o.matrix_world@v.co) for v in o.data.vertices]
body=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in body:o.matrix_world=world@o.matrix_world

before=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(terrace))
incoming=[o for o in bpy.context.scene.objects if o not in before]
# Import already converts glTF Y-up to Blender Z-up. Exactly one normalized-to-body translation.
fit=Matrix.Translation(Vector((-.10478019714355469,-1.3359999656677246,-.16432876884937286)))
for o in incoming:
    if o.parent not in incoming:o.matrix_world=world@fit@o.matrix_world
bpy.context.view_layer.update()
meshes=body+[o for o in incoming if o.type=='MESH']
# Visible terrain skirt only, down to measured pavement. This is an inferred
# integration closure, not a modeled underground foundation or a new walking surface.
stone=bpy.data.materials['03_Pale_mineral_platform']
outline=[(-6.2795,-1.784,0),(-5.953958414148326,-1.784,0),(-5.953958414148326,-1.784,-.164328769),(5.744397750235235,-1.784,-.164328769),(5.744397750235235,-1.784,0),(6.2795,-1.784,0),(6.2795,1.786,0),(-6.2795,1.786,0)]
verts=[];faces=[];skirt_depths=[]
for i,a in enumerate(outline):
    b=outline[(i+1)%len(outline)];a,b=Vector(a),Vector(b)
    if (Vector((a.x,a.y))-Vector((b.x,b.y))).length<.0001:continue
    steps=max(1,math.ceil((b-a).length/.25))
    for j in range(steps):
        ends=[world@a.lerp(b,t) for t in [j/steps,(j+1)/steps]]
        depths=[max(0,p.z-ground(p.x,p.y)+.001) for p in ends]
        if max(depths)<.0001:continue
        low=[Vector((p.x,p.y,p.z-d)) for p,d in zip(ends,depths)]
        v=len(verts);verts.extend([ends[0],ends[1],low[1],low[0]]);faces.append((v,v+1,v+2,v+3));skirt_depths.extend(depths)
me=bpy.data.meshes.new('BOX1_terrain_skirt_INFERRED');me.from_pydata(verts,[],faces);me.materials.append(stone)
skirt=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(skirt);meshes.append(skirt)
# Batch by material: no new textures or material edits; <=40 B-level draw primitives.
exports=[]
for material in sorted({m for o in meshes for m in o.data.materials},key=lambda m:m.name):
    bpy.ops.object.select_all(action='DESELECT')
    copies=[]
    for o in meshes:
        if len(o.data.materials)==1 and o.data.materials[0]==material:
            c=o.copy();c.data=o.data.copy();bpy.context.scene.collection.objects.link(c);c.select_set(True);copies.append(c)
    assert copies,material.name
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();c=bpy.context.object;c.name='BOX1_'+material.name;exports.append(c)
bpy.ops.object.select_all(action='DESELECT')
for o in exports:o.select_set(True)
out=R/'web/shibu-hachi-box.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False)
count=0
for o in exports:o.data.calc_loop_triangles();count+=len(o.data.loop_triangles)
points=[o.matrix_world@v.co for o in exports for v in o.data.vertices]
bounds=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
report={'base_commit':'4948a00','position_source':position_source,'origin_plan_xyz':list(origin),'yaw_degrees':math.degrees(yaw),'scale':[1,1,1], 'world_matrix_rows':[list(row) for row in world], 'inverse_matrix_rows':[list(row) for row in world.inverted()], 'terrace_normalized_to_body_blender':list(fit.translation),'ground_samples':samples,'anchor_tp':anchor+15,'ground_range_m':max(p['ground_y'] for p in samples)-min(p['ground_y'] for p in samples),'removed_components':removed,'selectively_cut':cut,'protected_components':list(protected),'protected_vertices_exact':True,'bounds_plan_xyz':bounds,'triangles':count,'primitives':len(exports),'bytes':out.stat().st_size,'sha256':sha(out)}
report['ground_fit']={'basis':'Visible R3 top 5mm above measured Core pavement; no geometry scaling, no ground/collision edits','r3_ground_y':terminal_ground,'r3_top_gap_m':.005,'inferred_visible_skirt_max_depth_m':max(skirt_depths),'skirt_is_foundation_evidence':False}
(R/'source/placement-and-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
hints={'planBounds':[bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]],'sun':{'azimuth_deg':145,'elevation_deg':42},'groundElevationTP':15}
(R/'web/viewer.json').write_text(json.dumps(hints,indent=2)+'\n')
for t in ['day','night']:(R/f'web/emissive_{t}.json').write_text('{}\n')
manifest={'id':'shibu-hachi-box','source_id':'way/1315939856','level':'B','status':'BOX-1 exterior/terrace estimate for review; not surveyed or full plaza completion','stats':{k:report[k] for k in ['triangles','primitives','bytes']},'files':{}}
for p in sorted(R.rglob('*')):
    if p.is_file() and p!=R/'manifest.json':manifest['files'][p.relative_to(R).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('BOX1_RESULT',json.dumps({k:report[k] for k in ['origin_plan_xyz','yaw_degrees','anchor_tp','ground_range_m','triangles','primitives','bytes']}))
