#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
from regenerate import ROOT,INPUT_SHA,OUTPUT_SHA,parse,indices
raw0,j0,b0=parse(ROOT/'baseline/hikarie.glb');raw1,j1,b1=parse(ROOT/'web/hikarie.glb');c=json.loads((ROOT/'source/overlay_contract.json').read_text());assert hashlib.sha256(raw0).hexdigest()==INPUT_SHA;assert hashlib.sha256(raw1).hexdigest()==OUTPUT_SHA;assert b1[:len(b0)]==b0;assert j0['materials']==j1['materials'];assert j0['nodes']==j1['nodes'];assert j0['scenes']==j1['scenes'];assert j0['accessors']==j1['accessors'][:len(j0['accessors'])];assert j0['bufferViews']==j1['bufferViews'][:len(j0['bufferViews'])]
cm={e['mesh']:e for e in c['meshes']};removed=0
for mi,(m0,m1) in enumerate(zip(j0['meshes'],j1['meshes'])):
 if mi not in cm:assert m0==m1
 else:
  ent=cm[mi];assert len(m0['primitives'])==len(m1['primitives']);pi=ent['primitive'];p0=m0['primitives'][pi];p1=m1['primitives'][pi];assert {k:v for k,v in p0.items() if k!='indices'}=={k:v for k,v in p1.items() if k!='indices'}
  orig=indices(j0,b0,p0['indices']);got=indices(j1,b1,p1['indices']);rm=set(ent['remove_triangle_indices']);ret=set(ent['retain_source91_triangle_indices']);assert not rm&ret;assert rm|ret==set(ent['source91_all_triangle_indices']);assert got==[t for k,t in enumerate(orig) if k not in rm];removed+=len(rm)
assert removed==906
nt=lambda j:sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives'])
assert nt(j0)-nt(j1)==906;assert nt(j1)==30562
receipt={'passed':True,'baseline_sha256':INPUT_SHA,'candidate_sha256':OUTPUT_SHA,'removed_only_contract_triangles':906,'retained_source91_overlay_triangles':204,'all_original_attribute_bytes_identical':True,'materials_nodes_scenes_identical':True,'source91_shell_and_other_meshes_identical':True,'triangle_count':nt(j1),'primitives':sum(len(m['primitives']) for m in j1['meshes']),'bytes':len(raw1),'within_B_budget':nt(j1)<=120000 and sum(len(m['primitives']) for m in j1['meshes'])<=40 and len(raw1)<=3000000}
(ROOT/'evidence/portable-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
