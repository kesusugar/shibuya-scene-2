from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
def snapshot():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();vv=[o.matrix_world@v.co for v in o.data.vertices];area=0.;live=0
  for tr in o.data.loop_triangles:
   a,b,c=[vv[i]for i in tr.vertices];aa=(b-a).cross(c-a).length*.5
   if aa>1e-9:live+=1;area+=aa
  if not vv:continue
  out[o.name]={'bounds_min':[min(p[i]for p in vv)for i in range(3)],'bounds_max':[max(p[i]for p in vv)for i in range(3)],'area_m2':area,'live_triangles':live}
 return out
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'parco_terrace_candidate.blend'));blend=snapshot();images=[im.name for im in bpy.data.images if im.source=='FILE'];assert not images,'Unexpected embedded/external reference image'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'parco_terrace_candidate.glb'));glb=snapshot();rows=[]
for name,a in blend.items():
 b=glb[name];bd=max(abs(x-y)for k in ['bounds_min','bounds_max']for x,y in zip(a[k],b[k]));ad=abs(a['area_m2']-b['area_m2']);rows.append({'mesh':name,'bounds_max_delta_m':bd,'surface_area_delta_m2':ad,'live_triangles_blend':a['live_triangles'],'live_triangles_glb':b['live_triangles'],'pass':bd<1e-4 and ad<.005})
report={'blend_sha256':hashlib.sha256((ROOT/'parco_terrace_candidate.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest(),'all_geometry_mesh_names_match':set(blend)==set(glb),'file_reference_images':images,'mesh_checks':rows,'all_pass':all(r['pass']for r in rows)and set(blend)==set(glb)}
(ROOT/'verification/saved-scene.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['all_pass']
