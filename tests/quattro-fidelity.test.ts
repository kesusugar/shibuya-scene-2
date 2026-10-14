import {expect,it} from 'vitest';
import {readFileSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3} from 'three';
import {LEVEL_BUDGET} from '../src/perf/budget';
const base='assets/buildings/quattro/';
const json=(p:string)=>JSON.parse(readFileSync(base+p,'utf8'));
const digest=(p:string)=>createHash('sha256').update(readFileSync(base+p)).digest('hex');
async function geometry(file='quattro.glb'){
 const root=(await new NodeIO().read(base+'web/'+file)).getRoot();
 return {root,parts:root.listNodes().flatMap(n=>(n.getMesh()?.listPrimitives()??[]).map(p=>{
  const a=p.getAttribute('POSITION')!,m=new Matrix4().fromArray(n.getWorldMatrix());
  const v=Array.from({length:a.getCount()},(_,i)=>new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m));
  return {name:n.getName(),material:p.getMaterial()!.getName(),v,indices:Array.from((p.getIndices()?.getArray()??v.map((_,i)=>i)) as ArrayLike<number>)};
 }))};
}
it('BIG ECHO identity correction leaves original raw source, source IDs, exact shell and datum intact',async()=>{
 expect(digest('source/data/plateau.json')).toBe('967dbde173f2b5920619b7b4eba017be79e1948c35afd7e8d3be2336f8f7ccd8');
 const {parts}=await geometry();const shell=json('source/data/original_shell.json');
 for(const [name,data] of Object.entries(shell) as [string,{vertices:number[][],faces:number[][]}][]){
  const p=parts.find(x=>x.name===name)!;expect(p).toBeTruthy();
  const key=(v:Vector3)=>v.toArray().map(n=>n.toFixed(4)).join(',');
  const actual=new Set<string>();for(let i=0;i<p.indices.length;i+=3)actual.add(p.indices.slice(i,i+3).map(j=>key(p.v[j])).sort().join('|'));
  for(const face of data.faces)expect(actual.has(face.map(j=>{const a=data.vertices[j];return key(new Vector3(a[0],a[2],-a[1]));}).sort().join('|'))).toBe(true);
 }
 expect(json('source/data/layout.json').name).toContain('21-8');expect(json('source/data/layout.json').source_id).toBe('way/136691389');
 expect(json('web/viewer.json').groundElevationTP).toBe(15);
 expect(Math.max(...parts.flatMap(p=>p.v.map(v=>v.y)))).toBeCloseTo(31.015,3);
});
it('BIG ECHO four low frontage tiers replace eight generic floors without glass on sloped/blank upper faces',async()=>{
 const {parts}=await geometry();const glass=parts.filter(p=>p.material.includes('glass')).flatMap(p=>p.v);
 expect(glass.length).toBeGreaterThan(0);expect(Math.max(...glass.map(v=>v.y))).toBeLessThanOrEqual(15.201);
 const l=json('source/data/layout.json');expect(l.frontage_glazing_z_m).toHaveLength(4);expect(l.floors).toBeUndefined();
 const s=json('source/data/stats.json');expect(s.glass_panels).toBe(24);expect(s.roof_translation_m).toBe(0);expect(s.blank_flanks).toBe(true);
});
it('BIG ECHO dated image layer is separate and unregistered; base has no textures or invented emission',async()=>{
 const {root}=await geometry();const e=(await geometry('signs-2025-01.glb')).root;
 expect(root.listTextures()).toHaveLength(0);expect(e.listTextures()).toHaveLength(2);expect(json('web/viewer.json').layers).toBeUndefined();
 for(const m of root.listMaterials())expect(m.getEmissiveFactor()).toEqual([0,0,0]);
 expect(e.listNodes().every(n=>n.getExtras().runtime_registered===false)).toBe(true);
});
type V=[number,number];
const cross=(a:V,b:V,c:V)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
function inside(p:V,ring:V[]){let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++)if((ring[i][1]>p[1])!==(ring[j][1]>p[1])&&p[0]<(ring[j][0]-ring[i][0])*(p[1]-ring[i][1])/(ring[j][1]-ring[i][1])+ring[i][0])yes=!yes;return yes;}
function crossing(a:V,b:V,c:V,d:V){return cross(a,b,c)*cross(a,b,d)<-1e-10&&cross(c,d,a)*cross(c,d,b)<-1e-10;}
it('every projected triangle remains outside protected QFRONT and Seibu footprints',async()=>{
 const protectedData=json('source/data/protected_footprints.json').footprints;
 const rings:V[][]=Object.values(protectedData).flatMap((g:any)=>g.type==='Polygon'?[g.coordinates[0]]:g.coordinates.map((p:any)=>p[0]));
 for(const f of ['quattro.glb','signs-2025-01.glb'])for(const p of (await geometry(f)).parts)for(let k=0;k<p.indices.length;k+=3){
  const tri=p.indices.slice(k,k+3).map(i=>[p.v[i].x,-p.v[i].z] as V);if(Math.abs(cross(...tri as [V,V,V]))<1e-9)continue;
  for(const ring of rings){
   const bx=ring.map(v=>v[0]),by=ring.map(v=>v[1]);if(Math.max(...tri.map(v=>v[0]))<Math.min(...bx)||Math.min(...tri.map(v=>v[0]))>Math.max(...bx)||Math.max(...tri.map(v=>v[1]))<Math.min(...by)||Math.min(...tri.map(v=>v[1]))>Math.max(...by))continue;
   expect(tri.some(v=>inside(v,ring))).toBe(false);expect(ring.some(v=>inside(v,tri))).toBe(false);
   for(let i=0;i<3;i++)for(let j=0;j<ring.length-1;j++)expect(crossing(tri[i],tri[(i+1)%3],ring[j],ring[j+1])).toBe(false);
  }
 }
});
it('BIG ECHO base and optional dated layers remain inside unchanged B budget',async()=>{
 let triangles=0,primitives=0,bytes=0;
 for(const f of ['quattro.glb','signs-2025-01.glb']){const {parts}=await geometry(f);primitives+=parts.length;triangles+=parts.reduce((s,p)=>s+p.indices.length/3,0);bytes+=statSync(base+'web/'+f).size;}
 expect(triangles).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);expect(primitives).toBeLessThanOrEqual(LEVEL_BUDGET.B.primitives);expect(bytes).toBeLessThanOrEqual(LEVEL_BUDGET.B.bytes);
 expect(json('source/data/stats.json').triangles+4).toBe(triangles);
});

it('BIG ECHO preserves distinct photo-supported lower hood, brown upper hood and crest opening above unchanged roof',async()=>{
 const {parts}=await geometry();
 for(const [name,z0,z1] of [['quattro_roof_lower_hood_details',20,24],['quattro_hood_brown_details',25,27],['quattro_roof_upper_opening_details',27,29.1]] as [string,number,number][]){
  const p=parts.find(p=>p.name===name)!;expect(p).toBeTruthy();expect(p.indices.length).toBeGreaterThanOrEqual(6);
  expect(Math.min(...p.v.map(v=>v.y))).toBeGreaterThan(z0);expect(Math.max(...p.v.map(v=>v.y))).toBeLessThan(z1);
 }
});

it('January blade front faces point southeast and artwork UVs are not mirrored from the outward side',async()=>{
 const root=(await new NodeIO().read(base+'web/signs-2025-01.glb')).getRoot();
 // Blender T=(11.624,-11.247,0), transformed to glTF (x,z,-y).
 const outward=new Vector3(11.624,0,11.247).normalize();
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  expect(p.getMaterial()!.getDoubleSided()).toBe(false);
  const pos=p.getAttribute('POSITION')!,uv=p.getAttribute('TEXCOORD_0')!,m=new Matrix4().fromArray(n.getWorldMatrix());
  const ix=Array.from(p.getIndices()!.getArray() as ArrayLike<number>);
  for(let k=0;k<ix.length;k+=3){
   const a=new Vector3().fromArray(pos.getElement(ix[k],[])).applyMatrix4(m),b=new Vector3().fromArray(pos.getElement(ix[k+1],[])).applyMatrix4(m),c=new Vector3().fromArray(pos.getElement(ix[k+2],[])).applyMatrix4(m);
   expect(b.clone().sub(a).cross(c.clone().sub(a)).normalize().dot(outward)).toBeGreaterThan(.999);
  }
  // Increasing U follows -N in plan, the viewer's right on the +T facing side; glTF flips texture V only.
  const rows=Array.from({length:pos.getCount()},(_,i)=>({v:new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(m),uv:uv.getElement(i,[])}));
  const l=rows.find(r=>r.uv[0]<.01)!,rr=rows.find(r=>r.uv[0]>.99&&Math.abs(r.v.y-l.v.y)<.01)!;
  expect(rr.v.clone().sub(l.v).normalize().dot(new Vector3(11.247,0,-11.624).normalize())).toBeGreaterThan(.999);
 }
});
