from clip import *
from collections import Counter
original,ob=parse((R/'input/ekimae.glb').read_bytes());final,fb=parse((R/'web/ekimae.glb').read_bytes())
assert fb[:len(ob)]==ob
assert final['nodes'][:len(original['nodes'])]==original['nodes']
assert final['materials'][:len(original['materials'])]==original['materials']
def triangles(d,b,minh=None):
 out=[]
 for mi,m in enumerate(d['meshes']):
  for pi,p in enumerate(m['primitives']):
   a={k:acc(d,b,v) for k,v in p['attributes'].items()};ix=[v[0] for v in acc(d,b,p['indices'])];mat=d['materials'][p['material']]['name']
   for j in range(0,len(ix),3):
    ids=ix[j:j+3]
    if minh is None or min(a['POSITION'][i][1] for i in ids)>=minh:out.append((mat,tuple(tuple((k,a[k][i]) for k in sorted(a)) for i in ids)))
 return Counter(out)
before=triangles(original,ob,3.15);after=triangles(final,fb,3.15);assert not (before-after)
# Accessor POSITION extrema used by every primitive are exact; including appended clipped-accessors.
wrong=[]
for mi,m in enumerate(final['meshes']):
 for pi,p in enumerate(m['primitives']):
  a=final['accessors'][p['attributes']['POSITION']];vs=acc(final,fb,p['attributes']['POSITION'])
  for field,fn in [('min',min),('max',max)]:
   v=[fn(p[k] for p in vs) for k in range(3)]
   if any(abs(v[k]-a[field][k])>1e-5 for k in range(3)):wrong.append((mi,pi,field))
assert not wrong
pins={p.name:sha(p.read_bytes()) for p in [R/'input/ekimae.glb',R/'input/signs-2025-11.glb',R/'input/viewer.json']}
assert pins['signs-2025-11.glb']=='cc0290df14ee341e1a5da575b22db80019717c6c70317d09c1377eb4702db7a5'
assert pins['viewer.json']=='c4dd09fe0be2f62d6f51210abfb8b2e4a126343873002890858fb43b0a55fc57'
def used_bounds(d,b):
 points=[]
 for m in d['meshes']:
  for p in m['primitives']:
   vs=acc(d,b,p['attributes']['POSITION']);ix=acc(d,b,p['indices']);points.extend(vs[i[0]] for i in ix)
 return [[fn(p[k] for p in points) for k in range(3)] for fn in [min,max]]
old_bounds=used_bounds(original,ob);new_bounds=used_bounds(final,fb);assert old_bounds==new_bounds
def budget(d,b):
 return {'triangles':sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives']),'meshes':len(d['meshes']),'primitives':sum(len(m['primitives']) for m in d['meshes']),'materials':len(d['materials']),'nodes':len(d['nodes'])}
budget_before=budget(original,ob);budget_after=budget(final,fb)
report={'status':'Review prototype; geometry preservation passed; photo correspondence NOT passed','input_pins':pins,'asset_budget_before':budget_before,'asset_budget_after':budget_after,'input_glb_bytes':(R/'input/ekimae.glb').stat().st_size,'candidate_glb_bytes':(R/'web/ekimae.glb').stat().st_size,'runtime_performance_validation':'Not run; no navigation/FPS changes or claim','candidate_sha256':sha((R/'web/ekimae.glb').read_bytes()),'original_and_candidate_used_geometry_bounds':old_bounds,'used_geometry_global_bounds_unchanged':True,'all_original_binary_bytes_preserved_as_prefix':True,'original_node_transforms_and_materials_unchanged':True,'upper_original_triangle_all_attributes_identical':sum(before.values()),'additional_upper_triangles_from_clipped_tall_faces':sum((after-before).values()),'all_used_POSITION_accessor_extrema_correct':True,'viewer_groundElevationTP':json.loads((R/'input/viewer.json').read_text())['groundElevationTP'],'no_sign_or_viewer_edits':True,'no_other_buildings_or_runtime_files_accessed_for_edit':True}
(R/'evidence/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
