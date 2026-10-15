"""Current lower-panel stage: exact pinned geometry, independent shape and seam checks."""
import collections, hashlib, json, struct
from pathlib import Path
import numpy as np
A=Path(__file__).resolve().parents[2]; D=A/'source/data'; B=D/'lower-panel-baseline'
E=A/'evidence/cumulative-v2/lower'; E.mkdir(parents=True,exist_ok=True)
BEFORE='75753aec0940ab0cdb1bc82914918adf424bef0098aad95c020a1b983a06b82c'
AFTER='e03535bbe29f29524354f76cb8f066b30072fe355abda503d2ddeb8f70f96b32'

def load(path):
    raw=path.read_bytes(); l=struct.unpack_from('<I',raw,12)[0]
    j=json.loads(raw[20:20+l]); buf=raw[28+l:]
    def arr(i):
        ac=j['accessors'][i]; bv=j['bufferViews'][ac['bufferView']]; n=3 if ac['type']=='VEC3' else 1
        return np.frombuffer(buf,dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[ac['componentType']],count=ac['count']*n,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0)).reshape(-1,n)
    data={}
    for mesh in j['meshes']:
        assert len(mesh['primitives'])==1
        p=mesh['primitives'][0]
        data[mesh['name']]={k:arr(v) for k,v in p['attributes'].items()}
        data[mesh['name']]['indices']=arr(p['indices']).reshape(-1,3)
    return raw,j,data

def key(pos,nor):
    # Cyclic rotations are equivalent; reverse winding is not.
    v=[pos[i].tobytes()+nor[i].tobytes() for i in range(3)]
    return min(tuple(v),tuple(v[1:]+v[:1]),tuple(v[2:]+v[:2]))

def counter(mesh):
    return collections.Counter(key(mesh['POSITION'][tri],mesh['NORMAL'][tri]) for tri in mesh['indices'])

raw0,j0,m0=load(B/'stream.glb'); raw1,j1,m1=load(A/'web/stream.glb')
assert hashlib.sha256(raw0).hexdigest()==BEFORE
assert hashlib.sha256(raw1).hexdigest()==AFTER
assert j0['materials']==j1['materials'] and j0['nodes']==j1['nodes']
for k in set(j0)|set(j1):
    if k not in ['meshes','accessors','bufferViews','buffers']: assert j0[k]==j1[k],k
assert len(j0['meshes'])==len(j1['meshes'])==8
for a,b in zip(j0['meshes'],j1['meshes']):
    assert a['name']==b['name']
    assert {k:v for k,v in a.items() if k!='primitives'}=={k:v for k,v in b.items() if k!='primitives'}
    for p,q in zip(a['primitives'],b['primitives']):
        assert {k:v for k,v in p.items() if k not in ['indices','attributes']}=={k:v for k,v in q.items() if k not in ['indices','attributes']}
changed='stream_spandrel'
for name in m0:
    if name==changed: continue
    for attr in m0[name]: assert m0[name][attr].tobytes()==m1[name][attr].tobytes(),(name,attr)
minus=counter(m0[changed])-counter(m1[changed]); plus=counter(m1[changed])-counter(m0[changed])
assert sum(minus.values())==6 and sum(plus.values())==12
old=m0[changed]; remove_ids=[594,597,600,1453,1456,1459]
expected_minus=collections.Counter(key(old['POSITION'][old['indices'][i]],old['NORMAL'][old['indices'][i]]) for i in remove_ids)
assert minus==expected_minus, 'Removed something besides the exact three legacy quads'
# Independent explicit shape oracle, not read from the build trace/report.
origin=np.array([255.985,-290.160,0.]); end=np.array([279.103,-264.434,0.]); width=np.linalg.norm(end-origin)
tangent=(end-origin)/width; normal=np.array([tangent[1],-tangent[0],0.]); high=90.804; low=75.240; pitch=5.188
rectangles=[(.075,.125,0,2),(.05,.1,2,3),(.225,.275,0,1),(.25,.30,1,3),(.45,.50,0,1),(.50,.55,1,3)]
expected_plus=collections.Counter(); quad_xyz=[]
for q0,q1,r0,r1 in rectangles:
    xyz=np.array([origin+tangent*(q*width)+normal*.19+[0,0,z] for q,z in [(q0,high-r1*pitch),(q1,high-r1*pitch),(q1,high-r0*pitch),(q0,high-r0*pitch)]])
    p=np.asarray(xyz[:,[0,2,1]]*[1,1,-1],dtype='<f4'); n=np.tile(np.asarray([normal[0],0,-normal[1]],dtype='<f4'),(4,1))
    for ids in [[0,1,2],[0,2,3]]: expected_plus[key(p[ids],n[ids])]+=1
    quad_xyz.append(p[:,[0,2,1]]*[1,-1,1])
assert plus==expected_plus, 'Current white rectangles differ from the six-photo-rectangle oracle'
# Geometric area and positive orientation of actual new triangles.
new=m1[changed]; new_xyz=[]; area=0.
for tri in new['indices']:
    p=new['POSITION'][tri]; n=new['NORMAL'][tri]
    if key(p,n) not in plus: continue
    xyz=p[:,[0,2,1]]*[1,-1,1]; cross=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])
    assert cross@normal>0
    assert np.max(np.abs((xyz-origin)@normal-.19))<3e-5
    assert xyz[:,2].min()>=low-1e-5 and xyz[:,2].max()<=high+1e-5
    area+=np.linalg.norm(cross)/2; new_xyz.append(xyz)
assert abs(area-80.74709474300633)<.002
# Polygon clipping in local q/z; confirms no positive-area overlap with retained plates.
def polygon_area(poly):
    if len(poly)<3:return 0.
    p=np.array(poly); return abs(np.dot(p[:,0],np.roll(p[:,1],-1))-np.dot(p[:,1],np.roll(p[:,0],-1)))/2

def clip(poly,axis,bound,keep_above):
    out=[]
    if not poly:return out
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ain=(a[axis]>=bound) if keep_above else (a[axis]<=bound)
        bin=(b[axis]>=bound) if keep_above else (b[axis]<=bound)
        if ain:out.append(a)
        if ain!=bin:
            f=(bound-a[axis])/(b[axis]-a[axis]); out.append(a+(b-a)*f)
    return out

coplanar=[]
for i,tri in enumerate(old['indices']):
    if i in remove_ids:continue
    xyz=old['POSITION'][tri][:,[0,2,1]]*[1,-1,1]
    if np.max(np.abs((xyz-origin)@normal-.19))<.001:
        coplanar.append(np.column_stack(((xyz-origin)@tangent/width,xyz[:,2])))
overlap=0.
for xyz in quad_xyz:
    qz=np.column_stack(((xyz-origin)@tangent/width,xyz[:,2])); q0,z0=qz.min(0); q1,z1=qz.max(0)
    for triangle in coplanar:
        poly=list(triangle)
        for ax,v,above in [(0,q0,True),(0,q1,False),(1,z0,True),(1,z1,False)]:poly=clip(poly,ax,v,above)
        overlap+=polygon_area(poly)*width
assert overlap<1e-6, ('Retained white-panel overlap',overlap)
for i,(a,b,r,s) in enumerate(rectangles):
    for c,d,u,v in rectangles[i+1:]:assert max(0,min(b,d)-max(a,c))*max(0,min(s,v)-max(r,u))==0
# Shared accepted upper/lower edge has identical float32 height, not a gap or z overshoot.
boundary=np.float32(high)
assert any(np.any(tri[:,1]==boundary) for tri in coplanar)
assert all(np.float32(x[:,2].max())==boundary for x,r in zip(quad_xyz,rectangles) if r[2]==0)
assert len(raw1)==2022104 and len(raw1)-len(raw0)==328
assert sum(len(v['indices']) for v in m1.values())==32538
stats0=json.loads((B/'stats.json').read_text()); stats1=json.loads((D/'stats.json').read_text())
for k in stats0:
    if k not in ['triangles','bytes','status','panel_revision','runtime_sha256','lower_panel_refinement']:assert stats0[k]==stats1[k],('stats',k)
assert stats1['runtime_sha256']==AFTER
assert stats1['panel_revision']['historical_stage_output_sha256']==BEFORE
assert {k:v for k,v in stats0['panel_revision'].items() if k!='runtime_sha256'}=={k:v for k,v in stats1['panel_revision'].items() if k!='historical_stage_output_sha256'}
assert stats1['triangles']==32538 and stats1['bytes']==2022104
assert stats1['datum_tp_m']==15 and stats1['missing_pavement_samples']==0 and len(stats1['pavement_samples'])==144
report=json.loads((D/'build-report.json').read_text())
assert report['output_sha256']==AFTER and report['source_sha256']==BEFORE
assert report['triangles_after']==32538 and report['triangle_delta']==6 and report['byte_delta']==328
result={'pass':True,'stage':'lower112-six-white-rectangles','baseline_sha256':BEFORE,'output_sha256':AFTER,
        'removed_exact_legacy_triangles':6,'added_traced_triangles':12,'triangles':32538,'glb_bytes':len(raw1),
        'triangle_delta':6,'byte_delta':328,'primitives':8,'materials_nodes_scene_unchanged':True,
        'all_other_mesh_accessor_bytes_unchanged':True,'all_retained_white_triangle_positions_normals_winding_exact':True,
        'accepted_upper_panels_and_spandrels_exact':True,'source98_118_and_other_faces_exact':True,
        'new_white_area_m2':area,'new_vs_retained_white_overlap_m2':overlap,'shared_boundary_z_float32_m':float(boundary),
        'new_rectangles_pairwise_overlap_m2':0,'shell_roof_ground_and_world_transform_exact':True,
        'ground_samples':144,'missing_ground_samples':0,'datum_tp_m':15}
(E/'tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
