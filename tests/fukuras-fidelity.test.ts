import { expect, it } from 'vitest';
import { readFileSync, statSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { LEVEL_BUDGET } from '../src/perf/budget';
const base='assets/buildings/fukuras/';
const json=(p:string)=>JSON.parse(readFileSync(base+p,'utf8'));
function glb(p:string){const b=readFileSync(base+p),n=b.readUInt32LE(12);return {d:JSON.parse(b.subarray(20,20+n).toString()),bin:b.subarray(28+n)};}
it('Fukuras preserves complete original shell/roof primitives and every original source buffer byte',()=>{
 const old=glb('source/data/baseline.glb'),now=glb('web/fukuras.glb');
 expect(now.bin.subarray(0,old.bin.length).equals(old.bin)).toBe(true);
 for(let i=0;i<old.d.meshes.length;i++) for(let j=0;j<old.d.meshes[i].primitives.length;j++){
  const a=old.d.meshes[i].primitives[j],b=now.d.meshes[i].primitives[j],name=old.d.materials[a.material].name;
  if(['fukuras_wall','fukuras_roof'].includes(name)) expect(b).toEqual(a);
  expect(b.attributes).toEqual(a.attributes);expect(b.material).toBe(a.material);
 }
 expect(now.d.nodes.slice(0,old.d.nodes.length)).toEqual(old.d.nodes);
 expect(now.d.materials.slice(0,old.d.materials.length)).toEqual(old.d.materials);
});
it('Fukuras bounded facade map keeps original datum and exact recorded ground samples',()=>{
 const s=json('source/data/stats.json'),old=json('source/data/baseline_stats.json'),map=json('source/data/facade_map.json');
 expect(s.pavement_samples).toEqual(old.pavement_samples);expect(s.missing_pavement_samples).toBe(0);
 expect(s.roof_translation_m).toBe(0);expect(s.source_top_tp).toBe(120.899);expect(s.datum_tp_m).toBe(15);
 expect(map.mask).toEqual([76,81,135]);expect(map.principal_field_source_z).toEqual([42.3,83.9]);
 expect(map.pieces.length).toBeGreaterThan(300);
 for(const p of map.pieces){expect(map.mask).toContain(p.surface);expect(p.depth_m).toBeGreaterThan(.03);expect(p.depth_m).toBeLessThanOrEqual(.25);expect(Math.max(...p.uv.map((v:number[])=>v[1]))).toBeLessThanOrEqual(83.9);}
 expect(map.pieces.some((p:any)=>p.material==='sign_housing')).toBe(false);
});
it('Fukuras actual export has outward nondegenerate finite new triangles, no textures and unchanged B limits',async()=>{
 const root=(await new NodeIO().read(base+'web/fukuras.glb')).getRoot();let tris=0,prims=0;
 for(const node of root.listNodes())for(const p of node.getMesh()?.listPrimitives()??[]){
  prims++;const pos=p.getAttribute('POSITION')!,norm=p.getAttribute('NORMAL')!,idx=p.getIndices()!;tris+=idx.getCount()/3;
  expect(p.getMaterial()!.getBaseColorTexture()).toBeNull();
  for(let i=0;i<pos.getCount();i++)expect(pos.getElement(i,[]).every(Number.isFinite)).toBe(true);
  if(!['curtain_glass','infill_silver','mullion_silver','circulation_glass','circulation_metal'].some(s=>p.getMaterial()!.getName()==='fukuras_'+s))continue;
  for(let i=0;i<idx.getCount();i+=3){const a=pos.getElement(idx.getScalar(i),[]),b=pos.getElement(idx.getScalar(i+1),[]),c=pos.getElement(idx.getScalar(i+2),[]),n=norm.getElement(idx.getScalar(i),[]);const u=b.map((v,j)=>v-a[j]),v=c.map((v,j)=>v-a[j]),cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];expect(cross.reduce((s,v,j)=>s+v*n[j],0)).toBeGreaterThan(0);}
 }
 const stats=json('source/data/stats.json');expect(tris).toBe(stats.triangles);expect(prims).toBe(stats.primitives);expect(tris).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);expect(prims).toBeLessThanOrEqual(LEVEL_BUDGET.B.primitives);expect(statSync(base+'web/fukuras.glb').size).toBeLessThanOrEqual(LEVEL_BUDGET.B.bytes);
});
it('Fukuras removes old overlay triangles only within the three verified surfaces and leaves no matching old strips',()=>{
 const old=glb('source/data/baseline.glb'),now=glb('web/fukuras.glb'),source=json('source/data/plateau.json');
 const read=(g:any,i:number)=>{const a=g.d.accessors[i],v=g.d.bufferViews[a.bufferView],w=a.type==='VEC3'?3:1,bytes=a.componentType===5123?2:4;return Array.from({length:a.count},(_,k)=>Array.from({length:w},(_,j)=>{const offset=(v.byteOffset??0)+(a.byteOffset??0)+k*(v.byteStride??w*bytes)+j*bytes;return a.componentType===5126?g.bin.readFloatLE(offset):bytes===2?g.bin.readUInt16LE(offset):g.bin.readUInt32LE(offset);}));};
 const faces=[76,81,135].map(si=>{const ring=source.surfaces[si].ring.slice(0,-1),o=ring[0],n=[0,0,0];for(let i=0;i<ring.length;i++){const p=ring[i],q=ring[(i+ring.length-1)%ring.length];n[0]+=(p[1]-q[1])*(p[2]+q[2]);n[1]+=(p[2]-q[2])*(p[0]+q[0]);n[2]+=(p[0]-q[0])*(p[1]+q[1]);}const length=Math.hypot(...n);for(let j=0;j<3;j++)n[j]/=length;if(n[1]<0)for(let j=0;j<3;j++)n[j]*=-1;const t=[n[1],-n[0],0],uv=(p:number[])=>[(p[0]-o[0])*t[0]+(p[1]-o[1])*t[1],p[2]],poly=ring.map(uv);return {o,n,t,uv,poly};});
 const inside=(p:number[],poly:number[][])=>{let yes=false;for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+poly.length-1)%poly.length];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;};
 let removed=0;
 for(let mi=0;mi<old.d.meshes.length;mi++)for(let pi=0;pi<old.d.meshes[mi].primitives.length;pi++){
 const a=old.d.meshes[mi].primitives[pi],b=now.d.meshes[mi].primitives[pi],name=old.d.materials[a.material].name;
 if(['fukuras_wall','fukuras_roof'].includes(name))continue;
 const verts=read(old,a.attributes.POSITION).map((v:number[])=>[v[0],-v[2],v[1]]),before=read(old,a.indices).flat(),after=read(now,b.indices).flat(),kept=new Set<string>();for(let k=0;k<after.length;k+=3)kept.add(after.slice(k,k+3).join(','));
 for(let k=0;k<before.length;k+=3){const ids=before.slice(k,k+3),vs=ids.map((i:number)=>verts[i]),c=[0,1,2].map(j=>vs.reduce((s:number,v:number[])=>s+v[j],0)/3);const target=c[2]<=83.9&&faces.some(f=>{const depth=c.reduce((s,v,j)=>s+(v-f.o[j])*f.n[j],0);return depth>.035&&depth<.25&&vs.every((v:number[])=>Math.abs(v.reduce((s,v,j)=>s+(v-c[j])*f.n[j],0))<.008)&&inside(f.uv(c),f.poly);});const present=kept.has(ids.join(','));if(!present){removed++;expect(target).toBe(true);}if(target)expect(present).toBe(false);}
 }
 expect(removed).toBeGreaterThan(3000);
});
