import {it,expect} from 'vitest';
import {NodeIO} from '@gltf-transform/core';
import {readFileSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Matrix4,Vector3} from 'three';
const base='assets/buildings/scramble-square/';
const json=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
const hash=(s:string)=>createHash('sha256').update(s).digest('hex');
const source=json(base+'source/data/plateau.json'),stats=json(base+'source/data/stats.json');
async function geometry(path:string){
 const root=(await new NodeIO().read(path)).getRoot();const triangles:{material:string;v:Vector3[]}[]=[];let primitives=0;
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  primitives++;expect(p.getMaterial()!.getBaseColorTexture()).toBeNull();
  const a=p.getAttribute('POSITION')!,index=p.getIndices(),m=new Matrix4().fromArray(n.getWorldMatrix());
  const count=index?index.getCount():a.getCount();
  for(let i=0;i<count;i+=3){const v=[0,1,2].map(k=>new Vector3().fromArray(a.getElement(index?index.getScalar(i+k):i+k,[])).applyMatrix4(m));expect(v.every(p=>[p.x,p.y,p.z].every(Number.isFinite))).toBe(true);triangles.push({material:p.getMaterial()!.getName(),v});}
 }
 return {root,triangles,primitives};
}
const serial=(tris:{material:string;v:Vector3[]}[])=>tris.map(t=>t.material+':'+t.v.map(p=>[p.x,p.y,p.z].map(v=>v.toFixed(5)).join(',')).sort().join(';')).sort().join('\n');
const repairs=[28,49,35,77].map(i=>({i,ring:source.surfaces[i].ring.map((p:number[])=>new Vector3(p[0],p[2],-p[1]))}));
const belongs=(t:{material:string;v:Vector3[]},r:Vector3[])=>t.v.every(v=>r.some(p=>p.distanceTo(v)<.002));
it('preserves every triangle except exact source faces 28, 49, 35 and 77',async()=>{
 const current=await geometry(base+'web/scramble-square.glb'),before=await geometry(base+'source/cumulative-v1/main.glb');
 const off=(ts:{material:string;v:Vector3[]}[])=>ts.filter(t=>!repairs.some(r=>belongs(t,r.ring)));
 expect(serial(off(current.triangles))).toBe(serial(off(before.triangles)));
 expect(current.triangles.length).toBe(before.triangles.length);
 for(const {i,ring:raw} of repairs){
  const ring=raw[0].distanceTo(raw[raw.length-1])<.002?raw.slice(0,-1):raw;
  const tris=current.triangles.filter(t=>belongs(t,ring));expect(tris.length).toBe(ring.length-2);
  const edges=new Map<string,number>();const N=new Vector3();
  for(let k=0;k<ring.length;k++)N.add(ring[k].clone().cross(ring[(k+1)%ring.length]));
  const area=N.length()/2;N.normalize();let sum=0;
  for(const t of tris){const ids=t.v.map(v=>ring.findIndex(p=>p.distanceTo(v)<.002));
   const cross=t.v[1].clone().sub(t.v[0]).cross(t.v[2].clone().sub(t.v[0]));
   expect(Math.abs(cross.clone().normalize().dot(N))).toBeGreaterThan(.999);sum+=cross.length()/2;
   for(let k=0;k<3;k++){const key=[ids[k],ids[(k+1)%3]].sort((a,b)=>a-b).join(',');edges.set(key,(edges.get(key)??0)+1);}
  }
  expect(Math.abs(sum-area)).toBeLessThan(.02);
  const boundary=ring.map((_,k)=>[k,(k+1)%ring.length].sort((a,b)=>a-b).join(',')).sort();
  expect([...edges].filter(([,n])=>n===1).map(([e])=>e).sort()).toEqual(boundary);
  expect([...edges.values()].every(n=>n===1||n===2)).toBe(true);
 }
 const roof=current.triangles.filter(t=>t.material==='scramble-square_roof').flatMap(t=>t.v);
 for(const f of source.surfaces.filter((f:{kind:string})=>f.kind!=='WallSurface'))for(const p of f.ring)expect(roof.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.002)).toBe(true);
});
it('preserves original datum and all 36 exact ground samples',()=>{
 const original=json(base+'source/data/pavement-baseline.json');expect(stats.pavement_samples).toEqual(original.pavement_samples);expect(stats.missing_pavement_samples).toBe(0);expect(stats.roof_translation_m).toBe(0);expect(stats.source_top_tp).toBe(243.637);expect(stats.source_id).toBe('way/617560918');expect(stats.glass_panels).toBeGreaterThan(100);
});
it('keeps north-only architectural features bounded, outward, and within unchanged B budgets',async()=>{
 const {triangles,primitives}=await geometry(base+'web/scramble-square.glb');
 expect(triangles.length).toBe(stats.triangles);expect(triangles.length).toBeLessThanOrEqual(120000);expect(primitives).toBeLessThanOrEqual(40);expect(statSync(base+'web/scramble-square.glb').size).toBeLessThanOrEqual(3000000);
 expect(stats.detailed_surface_indices).toEqual([77]);expect(stats.sweep.west_origin).toEqual([117.767,-104.738]);expect(stats.sweep.lower_width).toBeGreaterThan(stats.sweep.upper_width);expect(stats.sweep.z_range).toEqual([4,68]);expect(stats.sweep.retained_wall).toBe(true);
 expect(stats.slits.length).toBe(67);expect(new Set(stats.slits.map((s:number[])=>s[2]-s[1])).size).toBeGreaterThan(5);
 // Slot faces at offset 0.21 m must point outward, not through the retained wall.
 const N=new Vector3(-22.674/Math.hypot(54.656,22.674),0,-54.656/Math.hypot(54.656,22.674));const A=new Vector3(117.767,0,104.738);
 const slots=triangles.filter(t=>t.material==='scramble-square_dark'&&t.v.every(p=>Math.abs(p.clone().sub(A).dot(N)-.21)<.002));expect(slots.length).toBe(134);
 for(const t of slots)expect(t.v[1].clone().sub(t.v[0]).cross(t.v[2].clone().sub(t.v[0])).normalize().dot(N)).toBeGreaterThan(.999);
});

it('bounds every raised north feature to the stepped source wall, including slot heads',async()=>{
 const {triangles}=await geometry(base+'web/scramble-square.glb');const W=Math.hypot(54.656,22.674);const A=new Vector3(117.767,0,104.738),N=new Vector3(-22.674/W,0,-54.656/W),T=new Vector3(54.656/W,0,-22.674/W);
 let checked=0;
 for(const t of triangles)if(t.v.every(p=>{const d=p.clone().sub(A).dot(N);return d>.145&&d<.56;})){for(const p of t.v){const u=p.clone().sub(A).dot(T);expect(u).toBeGreaterThanOrEqual(-.002);expect(u).toBeLessThanOrEqual(W+.002);expect(p.y).toBeGreaterThanOrEqual(-.39);expect(p.y).toBeLessThanOrEqual((u<27.56?212.8:221.8)+.002);checked++;}}
 expect(checked).toBeGreaterThan(1000);
});
it('keeps the unlit screen divisions outside the swept fan and within the lower display',async()=>{
 const {root,triangles}=await geometry(base+'web/scramble-square.glb');const W=Math.hypot(54.656,22.674),A=new Vector3(117.767,0,104.738),N=new Vector3(-22.674/W,0,-54.656/W),T=new Vector3(54.656/W,0,-22.674/W);
 const mat=root.listMaterials().find(m=>m.getName()==='scramble-square_screen_backing')!;expect(mat).toBeDefined();expect(mat.getEmissiveFactor()).toEqual([0,0,0]);
 const screen=triangles.filter(t=>t.material==='scramble-square_screen_backing');expect(screen).toHaveLength(12);
 const seams=triangles.filter(t=>t.material==='scramble-square_spandrel'&&t.v.every(p=>{const d=p.clone().sub(A).dot(N);return d>.253&&d<.262;}));expect(seams.length).toBeGreaterThan(50);
 for(const t of [...screen,...seams])for(const p of t.v){expect(p.y).toBeGreaterThanOrEqual(3.999);expect(p.y).toBeLessThanOrEqual(28.001);}
 for(const t of seams)for(const p of t.v){const u=p.clone().sub(A).dot(T),z=p.y,k=Math.min(5,Math.floor((z-4)/4)),z0=4+4*k,z1=z0+4,f=(z-z0)/4;const sw=(h:number)=>6.2+24*((68-h)/64)**2;expect(u).toBeGreaterThan((1-f)*sw(z0)+f*sw(z1)+.199);}
});

it('pins the exact current-main comparison and accepted cumulative runtime',()=>{
 const blob=(p:string)=>{const b=readFileSync(base+p);return createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');};
 expect(blob('source/cumulative-v1/main.glb')).toBe('d834645cdb7eb500133a700ac7cd7ac56d684b77');
 expect(blob('web/scramble-square.glb')).toBe('ff02d1bf8234c0bde5af1a82b5729a3d9bbaf77f');
});
