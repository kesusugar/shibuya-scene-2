import json,struct,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'output/low_shrub.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n])
assert d['asset']['version']=='2.0';assert len(d['materials'])==2
assert d['materials'][1]['alphaMode']=='MASK';assert d['materials'][1]['doubleSided'];assert d['materials'][1].get('alphaCutoff',.5)==.5
assert all('uri' not in im for im in d['images']);assert len(d['images'])==1
pr=d['meshes'][0]['primitives'];assert len(pr)==2
tris=sum(d['accessors'][x['indices']]['count']//3 for x in pr);assert tris<=6000
positions=[d['accessors'][x['attributes']['POSITION']] for x in pr];lo=[min(a['min'][i] for a in positions) for i in range(3)];hi=[max(a['max'][i] for a in positions) for i in range(3)]
# glTF is Y-up; Blender Z maps to Y and Y to -Z.
assert abs(lo[1])<1e-6 and abs(lo[0]+hi[0])<1e-6 and abs(lo[2]+hi[2])<1e-6
assert all(math.isfinite(v) for a in positions for k in ['min','max'] for v in a[k])
report={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'triangles':tris,'primitives':len(pr),'materials':2,'embedded_images':1,'alpha_mode':'MASK','origin_verified':True,'gltf_bounds':[lo,hi],'scope':'module only, no runtime FPS acceptance'}
(root/'evidence/validation.json').write_text(json.dumps(report,indent=2));print(report)
