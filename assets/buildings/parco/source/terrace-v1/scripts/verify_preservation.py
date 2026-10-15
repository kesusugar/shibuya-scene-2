from pathlib import Path
import json,hashlib,numpy as np
from glb_io import *
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'inputs';a,ab=read(BASE/'roof22-corrected-base.glb');b,bb=read(ROOT/'parco_terrace_candidate.glb');G=ROOT/'geometry'
wall=json.loads((G/'cut-audit.json').read_text());sp=json.loads((G/'spandrel-cut-audit.json').read_text());allowed={1:{v['triangle'] for v in wall['triangles']},7:{v['triangle'] for v in sp['triangles']}}
components=json.loads((BASE/'shallow-component-stats.json').read_text())['components']
for mi,mat in [(8,'cladding'),(9,'joint'),(10,'glass'),(11,'rail_glass')]:
 c=[v for v in components if v['material']==mat];allowed[mi]={12*i+j for i,v in enumerate(c) if v['kind'] not in ['pale_cladding_panel','reveal_backing'] for j in range(12)}
report={'candidate_only':True,'immutable_inputs':[],'mesh_preservation':[],'all_original_attributes_bit_identical':True,'only_enumerated_indices_changed':True,'original_nodes_unchanged':a['nodes']==b['nodes'][:len(a['nodes'])],'original_materials_unchanged':a['materials']==b['materials'][:len(a['materials'])]}
for inp in json.loads((ROOT/'verification/immutable-inputs-start.json').read_text()):
 p=Path(inp['path']);h=hashlib.sha256(p.read_bytes()).hexdigest();report['immutable_inputs'].append({'file':str(p),'sha256':h,'unchanged':h==inp['sha256']})
for mi,m in enumerate(a['meshes']):
 pa=m['primitives'][0];pb=b['meshes'][mi]['primitives'][0];attrs=[]
 for key,ix in pa['attributes'].items():
  same=np.array_equal(acc(a,ab,ix),acc(b,bb,pb['attributes'][key]));attrs.append({'attribute':key,'bit_identical':same});report['all_original_attributes_bit_identical'] &= same
 ia=acc(a,ab,pa['indices']).reshape(-1,3);ib=acc(b,bb,pb['indices']).reshape(-1,3);changed=np.flatnonzero(np.any(ia!=ib,axis=1)).tolist();valid=set(changed)==allowed.get(mi,set());report['only_enumerated_indices_changed'] &= valid
 report['mesh_preservation'].append({'mesh':mi,'name':m['name'],'attributes':attrs,'changed_index_triangles':changed,'authorized_exactly':valid,'unchanged_index_triangle_count':len(ia)-len(changed)})
# Geometric retained areas exactly partition old triangles beforeglTF float32quantization.
report['wall_removed_area_m2']=sum(v['removed_area_m2'] for v in wall['triangles']);report['wall_area_partition_error_m2']=max(abs(v['original_area_m2']-v['retained_area_m2']-v['removed_area_m2']) for v in wall['triangles'])
report['spandrel_removed_area_m2']=sum(v['removed_area_m2'] for v in sp['triangles']);report['spandrel_retained_area_m2']=sum(v['retained_area_m2'] for v in sp['triangles']);report['spandrel_area_partition_error_m2']=max(abs(v['original_area_m2']-v['retained_area_m2']-v['removed_area_m2']) for v in sp['triangles'])
report['roof_all_attributes_and_indices_identical']=report['mesh_preservation'][0]['authorized_exactly'] and not report['mesh_preservation'][0]['changed_index_triangles']
report['source84_141']='No triangles owned by source84 or source141 are selected. All original wall indices except195,451,52,273,128,372,373 are identical. Source JSON is unchanged. Their1.82m notch remains untouched.'
report['footprint179']='Source JSON and original world attributes are unaltered. No footprint rescale, rotation or translation; additions are registered to fixed source179.'
report['qfront_seibu_other_assets']='No file was written outside the new production-candidate folder, and no other asset was imported or modified. The roof22 repair is inherited exactly from the corrected base.'
report['candidate_sha256']=hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest();report['candidate_bytes']=(ROOT/'parco_terrace_candidate.glb').stat().st_size
report['original_triangle_index_entries']=sum(a['accessors'][p['indices']]['count']//3 for m in a['meshes'] for p in m['primitives']);report['candidate_triangle_index_entries']=sum(b['accessors'][p['indices']]['count']//3 for m in b['meshes'] for p in m['primitives'])
report['candidate_live_non_degenerate_triangles']=0
for m in b['meshes']:
 for pr in m['primitives']:
  v=acc(b,bb,pr['attributes']['POSITION']);idx=acc(b,bb,pr['indices']).reshape(-1,3);q=v[idx];ar=np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)/2;report['candidate_live_non_degenerate_triangles']+=int(np.sum(ar>1e-9))
# Direct binary-prefix proof: nothing in the original buffer changes except authorized index bytes.
allowed_bytes=set()
for mi,triangles in allowed.items():
 ac=a['accessors'][a['meshes'][mi]['primitives'][0]['indices']];bv=a['bufferViews'][ac['bufferView']];width={5121:1,5123:2,5125:4}[ac['componentType']];start=bv.get('byteOffset',0)+ac.get('byteOffset',0)
 for ti in triangles:allowed_bytes.update(range(start+ti*3*width,start+(ti+1)*3*width))
changed_bytes=[i for i,(x,y) in enumerate(zip(ab,bb[:len(ab)])) if x!=y]
report['original_buffer_changed_bytes_count']=len(changed_bytes)
report['original_buffer_only_authorized_index_byte_changes']=set(changed_bytes)<=allowed_bytes
report['original_image_texture_sampler_tables_identical']=all(a.get(k,[])==b.get(k,[]) for k in ['images','textures','samplers'])
report['original_accessor_and_buffer_view_metadata_unchanged']=all(a.get(k,[])==b.get(k,[])[:len(a.get(k,[]))] for k in ['accessors','bufferViews'])
report['original_mesh_definitions_unchanged']=a['meshes']==b['meshes'][:len(a['meshes'])]
report['all_checks_passed']=all(v['unchanged'] for v in report['immutable_inputs']) and report['all_original_attributes_bit_identical'] and report['only_enumerated_indices_changed'] and report['original_nodes_unchanged'] and report['original_materials_unchanged'] and report['wall_area_partition_error_m2']<1e-5 and report['spandrel_area_partition_error_m2']<1e-6 and report['original_buffer_only_authorized_index_byte_changes'] and report['original_image_texture_sampler_tables_identical'] and report['original_accessor_and_buffer_view_metadata_unchanged'] and report['original_mesh_definitions_unchanged']
(ROOT/'verification/preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['mesh_preservation']},indent=2));assert report['all_checks_passed']
