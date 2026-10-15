"""Bound numerical changes in retained clipped fragments, without claiming a fused shell."""
from pathlib import Path
import json, hashlib, numpy as np
from glb_io import read,acc,world
ROOT=Path(__file__).resolve().parents[1]
d,b=read(ROOT/'parco_terrace_candidate.glb'); rows=[]
for filename,meshname in [('retained-wall-fragments.json','prototype_terrace_retained'),('retained-spandrel-fragments.json','prototype_terrace_retained_spandrel')]:
 fragments=json.loads((ROOT/'geometry'/filename).read_text()); ideal=np.array([p for f in fragments for p in f['vertices']],dtype=np.float64)
 p=next(m for m in d['meshes'] if m['name']==meshname)['primitives'][0];actual=world(acc(d,b,p['attributes']['POSITION'])).astype(np.float64)
 # Blender triangulation can split/merge attribute vertices. Coordinate sets must match float32 projections.
 quant=ideal.astype(np.float32).astype(np.float64); qs=set(map(tuple,quant)); aset=set(map(tuple,actual)); assert qs==aset
 delta=quant-ideal; maximum=float(np.linalg.norm(delta,axis=1).max()); assert maximum<.00002
 rows.append({'fragment_file':filename,'mesh':meshname,'all_serialized_coordinates_equal_float32_projection':True,'vertex_instances':len(ideal),'maximum_xyz_displacement_m':maximum,'maximum_axis_displacement_m':np.abs(delta).max(axis=0).tolist(),'loose_pairwise_displacement_bound_m':2*maximum})
report={'candidate_sha256':hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest(),'all_pass':True,'fragments':rows,'interpretation':'At most 0.0155 mm vertex displacement in the retained source-wall fragments and 0.0069 mm in retained spandrel fragments. The pairwise bound is a numeric upper bound if two originally coincident points quantize independently, not a measured whole-assembly seam width. Identical input coordinates quantize identically. This does not establish global watertightness or certify sub-mm architectural alignment.','weld_distinction':'The separate 0.1 mm welded-topology test is an edge-count test. It is not a numerical seam bound and not a Boolean-union/collision certificate.'}
(ROOT/'verification/retained-quantization.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
