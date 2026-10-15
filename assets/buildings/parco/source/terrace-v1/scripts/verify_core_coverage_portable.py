#!/usr/bin/env python3
"""Portable, standard-library-only exact coverage and retained-floor verification.
Run from any directory: python <copied-root>/scripts/verify_core_coverage_portable.py
Reads only the four local assets below. Writes verification/core-coverage-final.json.
Does not import, edit, or require any archival verifier, builder, or external workspace.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json, struct, hashlib, math, datetime
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_CANDIDATE_SHA='7338ad9fcebf455a82383f938c36d58d817b9a8b0e9b75ff1e3b88ad9e0d9179'
ASSETS=['inputs/frozen-terrace-layout.json','inputs/frozen-terrace-components.json','inputs/frozen-terrace-additions.glb','parco_terrace_candidate.glb']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
BEFORE={s:sha(ROOT/s) for s in ASSETS}
assert BEFORE['parco_terrace_candidate.glb']==EXPECTED_CANDIDATE_SHA, 'Candidate hash differs from this verification target'
L=json.loads((ROOT/ASSETS[0]).read_text(),parse_float=F,parse_int=F)
LOG=json.loads((ROOT/ASSETS[1]).read_text(),parse_float=F,parse_int=F)

def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area2(p): return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))
def area(p): return abs(area2(p))/2 if len(p)>=3 else F(0)
def ccw(p): return p if area2(p)>0 else list(reversed(p))
def onseg(p,a,b): return cross(a,b,p)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1])
def segments_meet(a,b,c,d):
 cs=[cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)]
 return (cs[0]*cs[1]<0 and cs[2]*cs[3]<0) or any([cs[0]==0 and onseg(c,a,b),cs[1]==0 and onseg(d,a,b),cs[2]==0 and onseg(a,c,d),cs[3]==0 and onseg(b,c,d)])
def simple(p):
 n=len(p)
 return len(set(p))==n and area(p)>0 and all(not segments_meet(p[i],p[(i+1)%n],p[j],p[(j+1)%n]) for i in range(n) for j in range(i+1,n) if j!=i+1 and not(i==0 and j==n-1))
def in_triangle(p,t): return all(cross(a,b,p)>=0 for a,b in zip(t,t[1:]+t[:1]))
def triangulate(p):
 p=ccw(p.copy()); inds=list(range(len(p))); ts=[]
 while len(inds)>3:
  for k,i in enumerate(inds):
   ia=inds[k-1];ic=inds[(k+1)%len(inds)];t=[p[ia],p[i],p[ic]]
   if cross(*t)>0 and not any(in_triangle(p[j],t) for j in inds if j not in [ia,i,ic]):
    ts.append(t);inds.pop(k);break
  else: raise RuntimeError('No exact nondegenerate ear')
 ts.append([p[i] for i in inds]);return ts

def clip(subject,clipper):
 """Exact Sutherland-Hodgman, both convex triangle polygons; closed half-planes."""
 out=ccw(subject.copy())
 for a,b in zip(ccw(clipper),ccw(clipper)[1:]+ccw(clipper)[:1]):
  inp=out;out=[]
  if not inp: break
  prev=inp[-1];dp=cross(a,b,prev)
  for curr in inp:
   dc=cross(a,b,curr)
   if (dc>=0)!=(dp>=0):
    t=dp/(dp-dc)
    out.append((prev[0]+t*(curr[0]-prev[0]),prev[1]+t*(curr[1]-prev[1])))
   if dc>=0: out.append(curr)
   prev,dp=curr,dc
  # Remove adjacent duplicates, retaining exact shared boundary points.
  out=[p for k,p in enumerate(out) if k==0 or p!=out[k-1]]
  if len(out)>1 and out[0]==out[-1]: out.pop()
 return out

def val(x): return {'decimal':float(x),'exact_rational':str(x)}
def pts(p): return [[str(a),str(b)] for a,b in p]
def prove(a,b,atr=None,btr=None):
 assert simple(a) and simple(b)
 at=atr if atr is not None else triangulate(a)
 bt=btr if btr is not None else triangulate(b)
 for p,t in [(a,at),(b,bt)]:
  assert sum(map(area,t))==area(p)
  assert all(area(clip(t[i],t[j]))==0 for i in range(len(t)) for j in range(i+1,len(t)))
  # Each triangle must sit in the verified ear-clipped polygon triangulation.
  ears=triangulate(p)
  assert all(sum(area(clip(tt,e)) for e in ears)==area(tt) for tt in t)
 rows=[]
 for i,t in enumerate(at):
  parts=[area(clip(t,u)) for u in bt]
  covered=sum(parts)
  assert covered==area(t)
  rows.append({'source_triangle_index':i,'source_triangle_xy_exact':pts(t),'area_m2':val(area(t)),'intersection_with_cover_triangles_m2':[val(q) for q in parts],'covered_area_m2':val(covered),'uncovered_area_m2':val(area(t)-covered)})
 inter=sum(F(r['covered_area_m2']['exact_rational']) for r in rows)
 assert inter==area(a)
 return {'method':'Exact rational ear clipping, pairwise convex triangle clipping against closed half-planes, exhaustive area equality per source triangle; no sampling and no numeric tolerance.', 'source_polygon_simple':True,'cover_polygon_simple':True,'source_triangle_count':len(at),'cover_triangle_count':len(bt),'source_area_m2':val(area(a)),'cover_area_m2':val(area(b)),'intersection_area_m2':val(inter),'uncovered_area_m2':val(area(a)-inter),'source_triangles_are_nonoverlapping':True,'cover_triangles_are_nonoverlapping':True,'each_triangulation_exhausts_its_polygon':True,'triangle_proof':rows,'cover_triangles_xy_exact':[pts(t) for t in bt]}


def quantize(x): return F(struct.unpack('<f',struct.pack('<f',float(x)))[0])
def canonical_triangle(t): return tuple(sorted(t))
def oriented_triangle(t): return min(tuple(t[i:]+t[:i]) for i in range(3))
def normal(t):
 a,b,c=t;u=tuple(b[i]-a[i] for i in range(3));v=tuple(c[i]-a[i] for i in range(3))
 return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
def read_glb(path):
 data=path.read_bytes();magic,ver,total=struct.unpack_from('<III',data)
 assert magic==0x46546c67 and ver==2 and total==len(data)
 pos=12;doc=None;blob=None
 while pos<len(data):
  ln,kind=struct.unpack_from('<II',data,pos);chunk=data[pos+8:pos+8+ln];pos+=8+ln
  if kind==0x4e4f534a: doc=json.loads(chunk)
  elif kind==0x004e4942: blob=chunk
 assert doc is not None and blob is not None
 return doc,blob
FORMATS={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}
WIDTH={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def accessor(doc,blob,i):
 a=doc['accessors'][i];assert 'sparse' not in a and not a.get('normalized',False)
 v=doc['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0
 n=WIDTH[a['type']];fmt='<'+FORMATS[a['componentType']]*n;size=struct.calcsize(fmt)
 off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
 return [struct.unpack_from(fmt,blob,off+k*stride) for k in range(a['count'])]
def load_terraces(path):
 doc,blob=read_glb(path);answer={}
 roots=doc['scenes'][doc.get('scene',0)]['nodes']
 for ni,node in enumerate(doc['nodes']):
  name=node.get('name','')
  if not name.startswith('prototype_terrace_'): continue
  assert ni in roots and not any(ni in n.get('children',[]) for n in doc['nodes'])
  assert not any(k in node for k in ['matrix','rotation','translation','scale'])
  mesh=doc['meshes'][node['mesh']];assert len(mesh['primitives'])==1
  p=mesh['primitives'][0];assert p.get('mode',4)==4
  assert doc['accessors'][p['attributes']['POSITION']]['componentType']==5126
  vertices=[(F(x),F(-z),F(y)) for x,y,z in accessor(doc,blob,p['attributes']['POSITION'])]
  ids=[v[0] for v in accessor(doc,blob,p['indices'])];assert len(ids)%3==0
  ts=[tuple(vertices[j] for j in ids[i:i+3]) for i in range(0,len(ids),3)]
  assert name not in answer
  answer[name]={'triangles':ts,'material':doc['materials'][p['material']]}
 return answer

def component(label):
 rows=[r for r in LOG if r['label']==label];assert len(rows)==1;return rows[0]
def check_prism(all_triangles,record):
 polygon=[tuple(quantize(v) for v in p) for p in record['plan']]
 z=list(map(quantize,record['z']))
 allowed={(x,y,h) for x,y in polygon for h in z}
 candidates=[t for t in all_triangles if all(v in allowed for v in t)]
 top=[t for t in candidates if all(v[2]==z[1] for v in t)]
 bottom=[t for t in candidates if all(v[2]==z[0] for v in t)]
 side_candidates=[t for t in candidates if t not in top and t not in bottom]
 ring=ccw(polygon)
 def outward_side(t):
  nx,ny,nz=normal(t)
  for a,b in zip(ring,ring[1:]+ring[:1]):
   if all((v[0],v[1]) in [a,b] for v in t): return nx*(b[1]-a[1])-ny*(b[0]-a[0])>0 and nz==0
  return False
 side=[t for t in side_candidates if outward_side(t)]
 ts=top+bottom+side;n=len(polygon)
 assert len(top)==n-2 and len(bottom)==n-2 and len(side)==2*n and len(ts)==4*n-4
 assert all(normal(t)[2]>0 for t in top) and all(normal(t)[2]<0 for t in bottom)
 edge_counts=Counter(tuple(sorted([a,b])) for t in ts for a,b in zip(t,t[1:]+t[:1]))
 assert all(k==2 for k in edge_counts.values())
 top2=[[v[:2] for v in t] for t in top];bottom2=[[v[:2] for v in t] for t in bottom]
 prove(polygon,polygon,top2,triangulate(polygon));prove(polygon,polygon,bottom2,triangulate(polygon))
 # Every side rectangle is covered in its entirety by exactly two triangles.
 side_proof=[]
 for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
  group=[t for t in side if all(v[:2] in [a,b] for v in t)];assert len(group)==2
  flat=[[(F(0) if v[:2]==a else F(1),v[2]) for v in t] for t in group]
  rect=[(F(0),z[0]),(F(1),z[0]),(F(1),z[1]),(F(0),z[1])]
  prove(rect,rect,flat,triangulate(rect))
  side_proof.append({'edge':i,'triangle_count':2,'full_normalized_side_rectangle_covered_exactly':True})
 return {'polygon':polygon,'z':z,'triangles':ts,'top':top2,'bottom':bottom2,'side':side,'report':{'label':record['label'],'total_triangle_count':len(ts),'top_triangle_count':len(top),'bottom_triangle_count':len(bottom),'side_triangle_count':len(side),'coordinate_welded_edge_count':len(edge_counts),'all_edges_have_two_incident_triangles':True,'top_bottom_normals_outward':True,'side_rectangles':side_proof,'oppositely_facing_neighbor_side_triangles_excluded':len(side_candidates)-len(side),'z_m':[val(x) for x in z],'thickness_m':val(z[1]-z[0])}}

frozen=load_terraces(ROOT/ASSETS[2]);candidate=load_terraces(ROOT/ASSETS[3]);assert set(frozen)==set(candidate)
oldfloor=frozen['prototype_terrace_floor'];newfloor=candidate['prototype_terrace_floor']
base_record=component('core_base');wrap_record=component('core_wrap_4F_floor');east_record=component('east_plaza_4F_floor')
assert base_record['plan']==L['core_polygon'] and wrap_record['plan']==L['corner_floor_polygon'] and east_record['plan']==L['east_floor_polygon']
base=check_prism(oldfloor['triangles'],base_record)
oldwrap=check_prism(oldfloor['triangles'],wrap_record)
newwrap=check_prism(newfloor['triangles'],wrap_record)
neweast=check_prism(newfloor['triangles'],east_record)
assert Counter(map(oriented_triangle,oldwrap['triangles']))==Counter(map(oriented_triangle,newwrap['triangles']))
removed_expected=Counter(map(canonical_triangle,base['triangles']))
delta=[]
for name in sorted(frozen):
 old=Counter(map(canonical_triangle,frozen[name]['triangles']));new=Counter(map(canonical_triangle,candidate[name]['triangles']))
 removed=old-new;added=new-old
 assert not added
 assert removed==(removed_expected if name=='prototype_terrace_floor' else Counter())
 # Preserve oriented triangle multiset too, not just unsigned coordinates.
 old_oriented=Counter(map(oriented_triangle,frozen[name]['triangles']));new_oriented=Counter(map(oriented_triangle,candidate[name]['triangles']))
 if name=='prototype_terrace_floor': old_oriented.subtract(Counter(map(oriented_triangle,base['triangles'])))
 assert +old_oriented==new_oriented
 delta.append({'mesh':name,'frozen_triangle_count':sum(old.values()),'candidate_triangle_count':sum(new.values()),'removed_triangle_count':sum(removed.values()),'added_triangle_count':sum(added.values()),'remaining_oriented_triangles_exactly_identical':True})
mat=newfloor['material'];pbr=mat.get('pbrMetallicRoughness',{});extensions=mat.get('extensions',{})
assert mat.get('alphaMode','OPAQUE')=='OPAQUE'
assert pbr.get('baseColorFactor',[1,1,1,1])[3]==1
assert extensions.get('KHR_materials_transmission',{}).get('transmissionFactor',0)==0
assert extensions.get('KHR_materials_diffuse_transmission',{}).get('diffuseTransmissionFactor',0)==0

layout_proof=prove([tuple(p) for p in L['core_polygon']],[tuple(p) for p in L['corner_floor_polygon']])
final_mesh_proof=prove(base['polygon'],newwrap['polygon'],base['top'],newwrap['top'])
assert newwrap['z'][0]<base['z'][0] and newwrap['z'][1]==base['z'][1]
assert wrap_record['z'][0]<base_record['z'][0] and wrap_record['z'][1]==base_record['z'][1]

# Actual per-vertex displacement, using exact decimal source coordinates and matched GLB positions.
def half_ulp(x):
 f=float(quantize(x));bits=struct.unpack('<I',struct.pack('<f',abs(f)))[0]
 current=F(struct.unpack('<f',struct.pack('<I',bits))[0])
 following=F(struct.unpack('<f',struct.pack('<I',bits+1))[0])
 previous=F(struct.unpack('<f',struct.pack('<I',bits-1))[0])
 return max(following-current,current-previous)/2
qreports=[]
for r,g,source in [(base_record,base,'frozen reference core_base, intentionally absent in candidate'),(wrap_record,newwrap,'current candidate retained core-wrap slab'),(east_record,neweast,'current candidate retained east-plaza slab')]:
 actual_vertices=set(v for t in g['triangles'] for v in t);rows=[]
 for i,xy in enumerate(r['plan']):
  for h in r['z']:
   original=tuple(xy)+ (h,);actual=tuple(map(quantize,original));assert actual in actual_vertices
   error=tuple(a-o for a,o in zip(actual,original));sq=sum(e*e for e in error);bounds=tuple(map(half_ulp,original))
   assert all(abs(e)<=b for e,b in zip(error,bounds))
   rows.append({'plan_vertex':i,'layout_xyz_m':[val(x) for x in original],'actual_glb_xyz_m':[val(x) for x in actual],'signed_error_xyz_m':[val(x) for x in error],'distance_squared_m2':val(sq),'distance_m':math.sqrt(float(sq)),'axis_half_ulp_bounds_m':[val(x) for x in bounds]})
 max_sq=max(F(v['distance_squared_m2']['exact_rational']) for v in rows)
 qreports.append({'label':r['label'],'measured_geometry':source,'vertex_count':len(rows),'max_axis_abs_error_m':[max(abs(v['signed_error_xyz_m'][k]['decimal']) for v in rows) for k in range(3)],'max_euclidean_displacement_m':math.sqrt(float(max_sq)),'max_euclidean_displacement_squared_exact_m2':str(max_sq),'max_per_axis_half_ulp_bound_m':[max(v['axis_half_ulp_bounds_m'][k]['decimal'] for v in rows) for k in range(3)],'vertices':rows})

# Exactly shared retained-floor seams, tested in actual candidate top, bottom and sides.
def boundary_edges(tris):
 counts=Counter(tuple(sorted([a,b])) for t in tris for a,b in zip(t,t[1:]+t[:1]))
 assert all(k in [1,2] for k in counts.values())
 return {edge for edge,k in counts.items() if k==1}
seams=[]
for ei,(a,b) in enumerate(zip(neweast['polygon'],neweast['polygon'][1:]+neweast['polygon'][:1])):
 for wi,(c,d) in enumerate(zip(newwrap['polygon'],newwrap['polygon'][1:]+newwrap['polygon'][:1])):
  if {a,b}!={c,d}: continue
  edge=tuple(sorted([a,b]));assert neweast['z']==newwrap['z']
  for g in [neweast,newwrap]:
   assert edge in boundary_edges(g['top']) and edge in boundary_edges(g['bottom'])
   face_ts=[t for t in g['side'] if all(v[:2] in [a,b] for v in t)];assert len(face_ts)==2
   assert set(v for t in face_ts for v in t)=={(*xy,z) for xy in [a,b] for z in g['z']}
  seams.append({'east_plan_edge':ei,'corner_plan_edge':wi,'actual_xy_endpoints_m':[[val(q) for q in a],[val(q) for q in b]],'actual_top_xyz_endpoints_m':[[val(q) for q in (*xy,newwrap['z'][1])] for xy in [a,b]],'actual_bottom_xyz_endpoints_m':[[val(q) for q in (*xy,newwrap['z'][0])] for xy in [a,b]],'same_endpoint_coordinates_exactly':True,'same_top_and_bottom_boundary_segments_exactly':True,'both_side_rectangles_complete':True,'endpoint_separation_m':0,'geometric_gap_on_this_entire_checked_seam_m':0,'basis':'Identical rational endpoint coordinates and z intervals; entire straight segment and side rectangle coincide, not a sample-point estimate.'})
assert len(seams)==2
AFTER={s:sha(ROOT/s) for s in ASSETS};assert BEFORE==AFTER
report={
 'status':'PASS','full_coverage_proved':True,'production_final_mesh_verified':True,'candidate_sha256':BEFORE[ASSETS[3]],
 'conclusion':'The actual candidate retains the complete closed core-wrap floor and opaque material. Relative to all seven frozen terrace meshes, only the exact 20 redundant core_base triangles are omitted. Complete core plan and z-volume containment is proved with exact arithmetic.',
 'inputs':BEFORE,'input_hashes_unchanged_after_verification':True,
 'method':{'arithmetic':'Exact rational arithmetic on literal JSON decimals and serialized IEEE-754 float32 values. Exhaustive triangulation/intersection, not sampling.','area_tolerance_m2':0,'coordinate_equality_tolerance_m':0,'z_tolerance_m':0,'glb_axes':'model x=glTF x; model y=-glTF z; model z=glTF y. Verified root nodes with no transforms or parents.'},
 'layout_plan_proof':layout_proof,'actual_candidate_surface_coverage_proof':final_mesh_proof,
 'retained_final_core_wrap_floor':newwrap['report'],'retained_final_east_plaza_floor':neweast['report'],'omitted_reference_core_base':base['report'],
 'volume_containment':{'entire_core_base_closed_solid_contained':True,'layout_core_base_z_m':[val(x) for x in base_record['z']],'layout_retained_slab_z_m':[val(x) for x in wrap_record['z']],'actual_core_base_z_m':[val(x) for x in base['z']],'actual_retained_slab_z_m':[val(x) for x in newwrap['z']],'actual_retained_extra_depth_m':val(base['z'][0]-newwrap['z'][0]),'uncovered_volume_m3':val(F(0))},
 'retained_floor_material':{'gltf_material':mat,'effective_alpha_mode':mat.get('alphaMode','OPAQUE'),'base_alpha':pbr.get('baseColorFactor',[1,1,1,1])[3],'transmission_factor':extensions.get('KHR_materials_transmission',{}).get('transmissionFactor',0),'opaque':True,'scope':'Serialized glTF material is opaque; application-specific runtime material replacement is outside this verifier.'},
 'terrace_mesh_delta':{'only_exact_core_base_20_triangles_removed':True,'all_remaining_oriented_terrace_triangles_unchanged':True,'meshes':delta,'scope':'All seven terrace meshes are compared in the final assembled candidate. Original building/base meshes are outside this geometry-delta assertion.'},
 'float32_quantization':{'scope':'Measured source-decimal to actual serialized GLB displacement for all vertices of the reference core-base slab and the current candidate core-wrap/east-plaza slabs. Not a whole-assembly clearance or gap test.','vertices_round_to_matched_glb_coordinates':True,'all_axis_errors_within_half_ulp':True,'max_measured_displacement_m':max(x['max_euclidean_displacement_m'] for x in qreports),'max_measured_displacement_mm':1000*max(x['max_euclidean_displacement_m'] for x in qreports),'components':qreports,'numeric_bound_caveat':'A coordinate quantization bound measures representation displacement only. It is not a bound on arbitrary assembly gaps, offsets, overlaps, missing interfaces, or runtime transforms.'},
 'checked_retained_floor_seams':{'seam_count':len(seams),'all_identical_exactly':True,'max_gap_on_only_these_two_verified_seams_m':0,'seams':seams,'scope':'Only the two entire shared boundary segments between east_plaza_4F_floor and core_wrap_4F_floor, with matching top, bottom and complete side rectangles. No claim that every interface in the building is gap-free.'},
 'limits':['Model geometry only; not as-built survey or structural adequacy.','Global assembly manifoldness, arbitrary component interfaces and existing-base preservation are not established by this floor proof.','The final floor material differs from the neutral prototype intentionally; it remains opaque.','The exact frozen triangle set proves redundant base removal; triangle soup is not a global Boolean-solid union.'],
 'portability':{'root_resolution':'Path(__file__).resolve().parents[1]','required_assets':ASSETS,'python_dependencies':'standard library only','external_workspace_or_archival_proof_required':False,'output':'verification/core-coverage-final.json'},
 'verifier_sha256':sha(Path(__file__)),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
output=ROOT/'verification/core-coverage-final.json';output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'candidate_sha256':report['candidate_sha256'],'full_coverage_proved':True,'production_final_mesh_verified':True,'core_layout_area_m2':layout_proof['source_area_m2']['decimal'],'core_serialized_area_m2':final_mesh_proof['source_area_m2']['decimal'],'uncovered_area_m2':0,'only_core_base_20_triangles_removed':True,'max_measured_quantization_displacement_m':report['float32_quantization']['max_measured_displacement_m'],'checked_shared_floor_seam_count':len(seams),'checked_shared_floor_seam_gap_m':0,'output':str(output)},indent=2))
