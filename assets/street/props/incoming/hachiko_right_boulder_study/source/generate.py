import bpy, bmesh, math, json, sys, random
from pathlib import Path
from mathutils import Vector
import numpy as np
OUT=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path(__file__).resolve().parents[1]
OUT.mkdir(parents=True,exist_ok=True);(OUT/'evidence').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
# Photo-informed rising right silhouette. All dimensions estimates; hidden underside/back invented.
xs=[-.43,-.36,-.26,-.12,.04,.19,.29,.36,.42]
heights=[.095,.16,.22,.32,.40,.52,.58,.55,.43]
N=32;M=18;v=[];f=[]
for back in [False,True]:
 for i in range(N+1):
  x=-.43+.85*i/N;h=float(np.interp(x,xs,heights))
  for j in range(M+1):
   t=j/M;z=h*t
   edge=0 if i in (0,N) else math.sin(math.pi*i/N)**.3; vert=0 if j in (0,M) else math.sin(math.pi*t)**.25
   depth=.235*edge*vert
   # broad front diagonal groove descending to left, rather than random sphere deformation
   line=.055+.37*(x+.43)/.85
   groove=.067*math.exp(-((z-line)/.025)**2)*edge*vert
   und=.008*math.sin(29*x+8*z)*math.sin(19*z-5*x)*edge*vert
   y=(depth*.75 if back else -depth+groove+und)
   v.append((x,y,z))
S=(N+1)*(M+1)
for b in range(2):
 for i in range(N):
  for j in range(M):
   a=b*S+i*(M+1)+j;c=a+M+1
   faces=[(a,c,a+1),(a+1,c,c+1)]
   f.extend([tuple(reversed(q)) if b else q for q in faces])
# Boundary coincident vertices joined into closed shell.
me=bpy.data.meshes.new('Photo-informed angular boulder');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('hachiko_right_boulder_study',me);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=.00001);bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
bm=bmesh.new();bm.from_mesh(me)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(abs(v.co.y)<1e-8 for v in f.verts)],context='FACES')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
# Center AABB at base; scale estimate width .85m / visible height .58m.
lo=Vector(tuple(min(v.co[k] for v in me.vertices) for k in range(3)));hi=Vector(tuple(max(v.co[k] for v in me.vertices) for k in range(3)))
shift=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for ve in me.vertices:ve.co-=shift
uv=me.uv_layers.new(name='Synthetic mineral projection')
for p in me.polygons:
 p.use_smooth=True
 for li in p.loop_indices:
  co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.425)/.85,co.z/.58)
# Self-authored deterministic mineral texture, no photographic pixels.
rng=np.random.default_rng(20250713);size=512
def noise(n):
 a=rng.random((n,n));axis=np.linspace(0,n-1,size);tmp=np.array([np.interp(axis,np.arange(n),row) for row in a]);return np.array([np.interp(axis,np.arange(n),col) for col in tmp.T]).T
fine=noise(210);mid=noise(70);broad=noise(12); yy,xx=np.mgrid[0:size,0:size]/size
spots=np.clip((fine*.55+mid*.45-.49)*4,0,1)
base=np.zeros((size,size,4),np.float32); brown=np.array([.28,.26,.23]);light=np.array([.49,.47,.42]);base[:,:,:3]=brown+(light-brown)*spots[:,:,None];base[:,:,:3]*=(.78+.35*broad[:,:,None]);base[:,:,:3]*=(1-.12*np.exp(-((yy-(.055+.37*xx)/.58)/.024)**2))[:,:,None];base[:,:,3]=1
im=bpy.data.images.new('Self-authored mineral mottling',width=size,height=size,alpha=True);im.pixels.foreach_set(base.ravel());im.filepath_raw=str(OUT/'mineral.png');im.file_format='PNG';im.save();im.pack();im.filepath="//mineral.png"
mat=bpy.data.materials.new('Dry gray brown mineral rock');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.89;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);o.data.materials.append(mat)
o['status']='Unplaced July 2025 photo-informed replacement study; continued 2026 existence unconfirmed'
o['dimensions']='Estimated .85m width, .58m height; depth and hidden faces inferred'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hachiko_right_boulder.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'hachiko_right_boulder.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
me.calc_loop_triangles();stats={'blender':bpy.app.version_string,'triangles':len(me.loop_triangles),'vertices':len(me.vertices),'dimensions_m':list(o.dimensions),'materials':1,'source_date':'2025-07-13','placement':'none','origin':'bottom AABB center'}
(OUT/'stats.json').write_text(json.dumps(stats,indent=2))
# Asset-only orthographic verification views; cameras/lights not exported.
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=720;sc.render.resolution_y=540;sc.render.resolution_percentage=100
sc.world.color=(.18,.18,.18);sc.view_settings.view_transform='AgX'
for loc,power,sz in [((-2,-3,4),450,3),((2,1,3),250,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=sz;l.rotation_euler=(Vector((0,0,.25))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.13
for name,loc in [('front',(0,-3,.53)),('side',(3,0,.53)),('oblique',(1.3,-3,1.0))]:
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.28))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(OUT/'evidence'/f'{name}.png');bpy.ops.render.render(write_still=True)
