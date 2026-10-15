"""Blender 4.2.3: extract original generator helpers without running its scene replacement."""
import bpy,bmesh,ast,math,json,struct
from pathlib import Path
from mathutils import Vector
assert bpy.app.version==(4,2,3)
ROOT=Path(__file__).resolve().parent.parent
original=ast.parse((ROOT/'source/facade_detail.py').read_text())
build=next(n for n in original.body if isinstance(n,ast.FunctionDef) and n.name=='build')
helpers=[n for n in build.body if isinstance(n,ast.FunctionDef) and n.name in ['point','surf','solid','beam']]
A=Vector((-62.416,-10.01,0));B=Vector((-46.78,-10.647,0));T=(B-A).normalized();N=Vector((-T.y,T.x,0))
CX,CY,R=-47.25,-19.25,8.72;END=math.radians(-8);curve=R*math.radians(98)
GROUP={}
def face(name,pts,uv=None,layer='base'):
 bm=GROUP.setdefault(name,bmesh.new());f=bm.faces.new([bm.verts.new(p) for p in pts]);f.normal_update()
exec(compile(ast.Module(body=helpers,type_ignores=[]),'original helpers','exec'))
def make(s):
 for ds in [-1.05,1.05]:solid(s+ds-.065,s+ds+.065,.12,2.85,'ek_gold',.15,.46)
 solid(s-1.1,s+1.1,2.8,3.02,'ek_gold',.15,.48)
 for ds in [-.16,.16]:
  p,n=point(s+ds,.39);beam((p.x,p.y,.85),(p.x,p.y,1.65),.045,'ek_silver')
def collect(s):
 GROUP.clear();make(s);result={}
 for material,bm in GROUP.items():
  bmesh.ops.triangulate(bm,faces=list(bm.faces));result[material]=[[[float(v.co.x),float(v.co.z),float(-v.co.y)] for v in f.verts] for f in bm.faces];bm.free()
 return result
out={'blender_version':bpy.app.version_string,'target':collect(curve+6.3),'first_door':collect(curve*.44),'T':list(T),'N':list(N)}
(ROOT/'source/signatures.json').write_text(json.dumps(out,indent=2)+'\n')
