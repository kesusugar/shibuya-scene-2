"""Blender 4.2.3. Run: blender -b --python source/build_low_shrub.py -- [output-dir].
One unplaced photo-informed low shrub; all dimensions and hidden branching inferred.
"""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+1 else ROOT/'output'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rng=random.Random(20261015)
materials=[]
for name,color in [('bark',(.105,.065,.035,1)),('needle_dark',(.035,.075,.018,1)),('needle_tip',(.105,.16,.035,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.88
 m.use_backface_culling=False;materials.append(m)
# Original procedural RGBA needle spray: no photograph or third-party texture.
N=256; pixels=[0.0]*(N*N*4); texrng=random.Random(917)
def line(x0,y0,x1,y1,width,color):
 steps=max(1,int(math.hypot(x1-x0,y1-y0)*1.6))
 for step in range(steps+1):
  t=step/steps;x=x0+(x1-x0)*t;y=y0+(y1-y0)*t;w=width*(1-t*.65)
  for yy in range(max(0,int(y-w-1)),min(N,int(y+w+2))):
   for xx in range(max(0,int(x-w-1)),min(N,int(x+w+2))):
    a=max(0,min(1,w+.5-math.hypot(xx-x,yy-y)));k=(yy*N+xx)*4
    if a>pixels[k+3]:pixels[k:k+4]=[*color,a]
for j in range(64):
 x0=128+texrng.uniform(-15,15);y0=texrng.uniform(25,85)
 angle=texrng.uniform(.22,math.pi-.22);length=texrng.uniform(70,155)
 x1=max(4,min(251,x0+math.cos(angle)*length));y1=min(251,y0+math.sin(angle)*length)
 tint=texrng.uniform(.75,1.3);line(x0,y0,x1,y1,texrng.uniform(.9,1.7),(.12*tint,.25*tint,.035*tint))
im=bpy.data.images.new('original_procedural_needle_spray',width=N,height=N,alpha=True);im.pixels=pixels
im.filepath_raw=str(OUT/'needle_spray.png');im.file_format='PNG';im.save();im.pack()
m=materials[1];bs=m.node_tree.nodes.get('Principled BSDF');node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);clip=m.node_tree.nodes.new('ShaderNodeMath');clip.operation='ROUND';m.node_tree.links.new(node.outputs['Alpha'],clip.inputs[0]);m.node_tree.links.new(clip.outputs[0],bs.inputs['Alpha']);m.surface_render_method='DITHERED';m.use_backface_culling=False
# glTF exporter reads alpha threshold through legacy blend_method in 4.2.
m.blend_method='CLIP';m.alpha_threshold=.4
verts=[];faces=[];slots=[]
def face(points,slot):
 k=len(verts);verts.extend([tuple(p) for p in points]);faces.append(tuple(range(k,k+len(points))));slots.append(slot)
def branch(p,q,r0,r1,n=6):
 p,q=Vector(p),Vector(q);d=(q-p).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.001:u=Vector((1,0,0))
 u.normalize();v=d.cross(u).normalized()
 for j in range(n):
  a=j*math.tau/n;b=(j+1)*math.tau/n
  a0=p+(u*math.cos(a)+v*math.sin(a))*r0;b0=p+(u*math.cos(b)+v*math.sin(b))*r0
  a1=q+(u*math.cos(a)+v*math.sin(a))*r1;b1=q+(u*math.cos(b)+v*math.sin(b))*r1
  face([a0,b0,b1,a1],0)
 face([p+(u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n))*r0 for j in reversed(range(n))],0)
 face([q+(u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n))*r1 for j in range(n)],0)
def spray(p,angle):
 p=Vector(p)
 for j in range(3):
  a=angle+j*math.pi/3;side=Vector((math.cos(a),math.sin(a),0))*.11
  up=Vector((math.cos(a)*.018,math.sin(a)*.018,.16))
  face([p-side,p+side,p+side+up,p-side+up],1)
# Irregular tapered woody stem, no opaque spherical foliage cores.
stem=[(0,0,0),(.018,.008,.22),(-.015,.018,.46),(.008,.012,.7),(-.012,.018,.91)]
for i in range(4):branch(stem[i],stem[i+1],.022-i*.0038,.018-i*.004,8)
pads=[(-.25,.035,.39,.20),(.23,.04,.49,.21),(-.08,-.15,.58,.23),(-.26,.04,.71,.20),(.23,.10,.76,.22),(.02,-.08,.85,.25),(-.12,.12,.95,.21),(.13,.015,1.02,.18)]
for i,(x,y,z,rad) in enumerate(pads):
 center=Vector((x,y,z));fork=Vector((.005,.012,z*.53))
 branch(fork,center,.011,.004,7)
 # Short branching sprays within each asymmetrical horizontal foliage pad.
 for j in range(20):
  angle=rng.uniform(0,math.tau);r=rad*math.sqrt(rng.random());off=Vector((math.cos(angle)*r,math.sin(angle)*r*.8,rng.uniform(-.025,.035)))
  end=center+off;branch(center,end,.0035,.0010,5)
  spray(end-Vector((0,0,.03)),rng.uniform(0,math.tau))
mesh=bpy.data.meshes.new('low_shrub_mesh');mesh.from_pydata(verts,[],faces);mesh.materials.clear()
for m in materials[:2]:mesh.materials.append(m)
uv=mesh.uv_layers.new(name='UVMap')
for p,s in zip(mesh.polygons,slots):
 p.material_index=s;p.use_smooth=(s==0)
 if s==1:
  for li,coord in zip(p.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=coord
ob=bpy.data.objects.new('hachiko_low_shrub_unplaced',mesh);bpy.context.collection.objects.link(ob)
# Bottom-centre origin means mesh AABB XY midpoint at zero, lowest Z zero.
mins=[min(v.co[i] for v in mesh.vertices) for i in range(3)];maxs=[max(v.co[i] for v in mesh.vertices) for i in range(3)]
shift=Vector(((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,mins[2]))
for v in mesh.vertices:v.co-=shift
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.export_scene.gltf(filepath=str(OUT/'low_shrub.glb'),export_format='GLB',use_selection=True,export_yup=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'low_shrub.blend'))
tri=sum(len(p.vertices)-2 for p in mesh.polygons)
assert tri<=6000
(OUT/'stats.json').write_text(json.dumps({'blender':bpy.app.version_string,'triangles':tri,'materials':2,'dimensions_m':[maxs[i]-mins[i] for i in range(3)],'origin':'AABB bottom centre','inferred':True,'placement':'none','original_stem_offset_in_centered_mesh':list(-shift)},indent=2))
