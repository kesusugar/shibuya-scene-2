"""Read original generator, record face-call provenance, without saving or exporting it."""
import bpy,bmesh,sys,ast,json,traceback,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SRC=R/'input/original'
assert bpy.app.version==(4,2,3)
build=SRC/'blender/build_ekimae.py'
text=build.read_text().split('objects=[]')[0].replace('if texture:', 'if False:')
# Label each original polygon; Blender propagates the label through triangulation.
text=text.replace('f=bm.faces.new', 'tag=bm.faces.layers.int.get("source_face") or bm.faces.layers.int.new("source_face");f=bm.faces.new');text=text.replace('f.normal_update()','f.normal_update(); f[tag]=len(RECORDS); RECORDS.append({"material":name,"layer":layer,"calls":[[Path(q.filename).name,q.lineno,q.line] for q in traceback.extract_stack()[-6:-1]]})',1)
sys.argv=['blender','--',str(SRC/'data/plateau.json'),str(SRC/'data/facades.json'),'unused',str(R/'evidence'),'--recorded-ground']
g={'__file__':str(build),'RECORDS':[],'traceback':traceback}
exec(compile(text,str(build),'exec'),g)
def key(ps):return '|'.join(','.join(f'{c:.4f}' for c in p) for p in sorted(tuple(round(c,4) for c in p) for p in ps))
rows={}
for (layer,mat),bm in g['GROUP'].items():
 if layer!='base':continue
 tag=bm.faces.layers.int.get('source_face');bmesh.ops.triangulate(bm,faces=list(bm.faces))
 for f in bm.faces:
  k=key([(float(v.co.x),float(v.co.z),float(-v.co.y)) for v in f.verts]);rows.setdefault(mat,{}).setdefault(k,[]).append(f[tag])
(R/'evidence/generator-provenance.json').write_text(json.dumps({'faces':g['RECORDS'],'triangles':rows},separators=(',',':')))
print('Recorded',len(g['RECORDS']),'original faces')
