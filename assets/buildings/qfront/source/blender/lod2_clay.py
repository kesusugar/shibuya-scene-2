# Clay render of the PLATEAU LOD2 QFRONT surfaces: the dimensional ground truth for the build.
import bpy, json, sys, math
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:]
data=json.load(open(argv[0])); out=argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
B=lambda x,y,z:(x,-z,y)       # scene (X east, Y up, Z south) -> Blender (X east, Y north, Z up)
cols={'WallSurface':(.82,.82,.8,1),'RoofSurface':(.95,.55,.35,1),'GroundSurface':(.4,.4,.4,1)}
for kind,polys in data['surfaces'].items():
    me=bpy.data.meshes.new(kind);verts=[];faces=[]
    for p in polys:
        q=p[:-1] if p[0]==p[-1] else p
        base=len(verts);verts+= [B(*v) for v in q];faces.append(list(range(base,base+len(q))))
    me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(kind,me);sc.collection.objects.link(ob)
    m=bpy.data.materials.new(kind);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=cols[kind];me.materials.append(m)
# ground plane
bpy.ops.mesh.primitive_plane_add(size=200,location=(-12,42,0))
sc.world=bpy.data.worlds.new('w');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.8,.9,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
sun=bpy.data.lights.new('sun','SUN');sun.energy=3.5;so=bpy.data.objects.new('sun',sun);sc.collection.objects.link(so);so.rotation_euler=(math.radians(50),0,math.radians(-35))
cam=bpy.data.cameras.new('cam');co=bpy.data.objects.new('cam',cam);sc.collection.objects.link(co);sc.camera=co
views={'axo':((48,32,58),(-12,44,22),35),'refa':(B(-12.6,10.2,68.2),B(0.8,16.2,-30.7),None),'top':((-12,43,140),(-12,43.01,0),None)}
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.render.resolution_x=960;sc.render.resolution_y=720
for name,(pos,tgt,lens) in views.items():
    co.location=Vector(pos);d=Vector(tgt)-Vector(pos);co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    cam.type='PERSP';cam.lens=lens or 22
    if name=='top':cam.type='ORTHO';cam.ortho_scale=45
    if name=='refa':cam.sensor_fit='VERTICAL';cam.angle_y=math.radians(52.2)
    sc.render.filepath=out+'_'+name+'.png';bpy.ops.render.render(write_still=True)
