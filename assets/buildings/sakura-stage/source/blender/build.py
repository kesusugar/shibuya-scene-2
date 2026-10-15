"""Bounded east113 correction on the accepted north143 dependency. Python 3 stdlib.
Only four synthetic X overlays are suppressed. December 2025 is later than the
October target; static-facade inference, approximate registration, not certification.
Run python source/blender/build.py [output.glb]. No terrain or shell regeneration.
"""
import json,sys,hashlib,copy,math
from pathlib import Path
from build_north143 import load,accessor,append_accessor,write,source
A=Path(__file__).resolve().parents[2]
BASE_SHA='25eecd5e60bd463efcb7cf133815de413633c93abf0dd7547c246f6d06386881'
# Offsets refer to triangles of the pinned accepted frame index stream, not vertices.
REMOVED_OFFSETS=list(range(1833,1841))+list(range(8538,8546))
ROWS=[24,27,30,33]
def main(output):
 baseline=A/'source/data/accepted-north143.glb'
 assert hashlib.sha256(baseline.read_bytes()).hexdigest()==BASE_SHA
 d,b=load(baseline);key=json.loads((A/'source/data/east113-source-key.json').read_text())
 p=next(x for x in d['meshes'] if x['name']=='sakura-stage_frame')['primitives'][0]
 ids=[x[0] for x in accessor(d,b,p['indices'])];pos=accessor(d,b,p['attributes']['POSITION']);records=[]
 for ti in REMOVED_OFFSETS:
  tri=ids[ti*3:ti*3+3];pts=[source(pos[i]) for i in tri];zmin=min(v[2] for v in pts);zmax=max(v[2] for v in pts)
  matches=[(i,v) for i,v in enumerate(key['current_X_brace_rows']) if i in (4,5,6,7) and abs(v['z'][0]-zmin)<.04 and abs(v['z'][1]-zmax)<.04]
  assert len(matches)==1,(ti,pts);i,v=matches[0]
  # Every vertex must lie at one of the two strip endpoints, .18m off source113.
  n=key['outward_normal'];xy=[v['xy0'],v['xy1']]
  assert all(min(math.dist(pt[:2],(e[0]+n[0]*.18,e[1]+n[1]*.18)) for e in xy)<.06 for pt in pts)
  records.append({'triangle_offset':ti,'indices':tri,'brace_index_zero_based':i,'generator_row':v['row'],'source_z_actual':[zmin,zmax]})
 assert {i:sum(r['brace_index_zero_based']==i for r in records) for i in (4,5,6,7)}=={4:4,5:4,6:4,7:4}
 kept=[(v,) for i,v in enumerate(ids) if i//3 not in REMOVED_OFFSETS]
 p['indices']=append_accessor(d,b,kept,'SCALAR',5125)
 write(d,b,output)
 counts={'triangles':sum(d['accessors'][p['indices']]['count']//3 for mesh in d['meshes'] for p in mesh['primitives']),'primitives':sum(len(m['primitives']) for m in d['meshes']),'bytes':Path(output).stat().st_size}
 assert counts['triangles']==31834 and counts['primitives']==12 and counts['bytes']<=3000000
 report={'dependency_sha256':BASE_SHA,'surface':113,'removed_brace_indices':[4,5,6,7],'removed_generator_rows':ROWS,'removed_triangles':records,'retained_unresolved_braces':[0,1,2,3],'stats':counts,'unchanged_budget':{'triangles':120000,'primitives':40,'bytes':3000000},'evidence_capture':'2025-12-01','limits':'December evidence is later than October2025 target; approximate photo registration and accepted static-facade inference; October state unverified. No full-facade or full-scene certification. Lower four X overlays remain unresolved, not validated real structure.'}
 Path(output).with_suffix('.east113-upper.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else A/'web/sakura-stage.glb')
