/** LIVE revision3 regressions. Historical canopy/panel fixtures are tested separately.
 * Contract contains bounded predecessor triangle ordinals and geometry fingerprints,
 * deliberately not mutable generator reports or workflow-status receipts.
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { Mesh, MeshStandardMaterial, Vector3, Ray } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { loadBuilding, applyEmissive, type EmissiveTable } from '../src/world/buildings';
import { classify, applyLook, LOOK_DEFAULT } from '../src/world/look';
const base='assets/buildings/shibuya109/';
const sha=(b: Uint8Array|string)=>createHash('sha256').update(b).digest('hex');
const contractBytes=readFileSync('tests/fixtures/shibuya109-revision3-contract.json');
const C=JSON.parse(contractBytes.toString());
function parse(data:Buffer){const n=data.readUInt32LE(12);return {j:JSON.parse(data.subarray(20,20+n).toString()),b:data.subarray(28+n)};}
const priorBytes=readFileSync(base+'source/entrance-panel-v1/output/shibuya109.glb'),liveBytes=readFileSync(base+'web/shibuya109.glb');
const prior=parse(priorBytes),live=parse(liveBytes);
function raw(g:ReturnType<typeof parse>,i:number){const a=g.j.accessors[i],v=g.j.bufferViews[a.bufferView];const size=({SCALAR:1,VEC2:2,VEC3:3,VEC4:4} as any)[a.type]*({5121:1,5123:2,5125:4,5126:4} as any)[a.componentType];return Buffer.concat(Array.from({length:a.count},(_,k)=>g.b.subarray((v.byteOffset??0)+(a.byteOffset??0)+k*(v.byteStride??size),(v.byteOffset??0)+(a.byteOffset??0)+k*(v.byteStride??size)+size)));}
function values(g:ReturnType<typeof parse>,i:number){const r=raw(g,i),a=g.j.accessors[i],n=({5121:1,5123:2,5125:4,5126:4} as any)[a.componentType];return Array.from({length:r.length/n},(_,k)=>a.componentType===5126?r.readFloatLE(k*n):r.readUIntLE(k*n,n));}
const retained=new Set<number>(Object.values(C.meshMap) as number[]);
async function loaded(bytes:Buffer){return loadBuilding('shibuya109',{loadGlb:async()=> (await new GLTFLoader().parseAsync(Uint8Array.from(bytes).buffer,'')).scene,loadJson:async u=>JSON.parse(readFileSync(base+'web/'+u.split('/').at(-1),'utf8'))});}
function rows(root:any,table:EmissiveTable){const out:any[]=[];root.traverse((o:any)=>{if(!o.isMesh)return;for(const m of Array.isArray(o.material)?o.material:[o.material])out.push({mesh:o.name,material:m.name,type:m.type,class:classify(m,o.name,table),color:m.color.toArray(),emissive:m.emissive.toArray(),emissiveIntensity:m.emissiveIntensity,metalness:m.metalness,roughness:m.roughness,opacity:m.opacity,transparent:m.transparent,depthWrite:m.depthWrite,depthTest:m.depthTest,side:m.side,envMapIntensity:m.envMapIntensity,map:m.map===null,emissiveMap:m.emissiveMap===null,vertexColors:m.vertexColors});});return out;}
describe('SHIBUYA109 LIVE revision3 preservation and application runtime',()=>{
 it('pins accepted live bytes, independent contract and canonical predecessor',()=>{
  expect(sha(contractBytes)).toBe('1dcad9c511adb6b40a3dfda40d100caaec53958fbfb5255cee18bb91dc6153aa');
  expect(sha(liveBytes)).toBe('0ef0583ab368e3d2265aa299292bd6306ef68901e859265b94f214090d8b239e');
  expect(sha(priorBytes)).toBe('a31e295bf8ce9bbef9ddc0c6164526db84cb7b08a6caf1957352be142854db90');
 });
 it('preserves every surviving attribute including COLOR_0 and exact retained indices under repack',()=>{
  let colors=0,removedTotal=0;
  for(const [mi,m] of prior.j.meshes.entries()){
   const p=m.primitives[0],ids=values(prior,p.indices),removed=new Set<number>();
   for(const [a,b] of C.removed[mi]??[]){expect(a).toBeGreaterThanOrEqual(0);expect(b).toBeLessThan(ids.length/3);for(let t=a;t<=b;t++)removed.add(t);}
   removedTotal+=removed.size;
   const expected=ids.filter((_:number,k:number)=>!removed.has(Math.floor(k/3)));
   if(!expected.length){expect(C.meshMap[mi]).toBeUndefined();continue;}
   const mesh=live.j.meshes[C.meshMap[mi]];expect(mesh.name).toBe(m.name);expect(mesh.primitives).toHaveLength(m.primitives.length);const q=mesh.primitives[0];
   expect(values(live,q.indices),m.name).toEqual(expected);expect(q.material).toBe(p.material);
   expect(Object.keys(q.attributes).sort()).toEqual(Object.keys(p.attributes).sort());
   for(const [semantic,ai] of Object.entries(p.attributes)){expect(raw(live,q.attributes[semantic]),m.name+':'+semantic).toEqual(raw(prior,ai as number));if(semantic==='COLOR_0')colors++;}
  }
  expect(colors).toBeGreaterThan(0);expect(removedTotal).toBe(1031);
  for(const name of ['shibuya109_roof','shibuya109_cap_shadow','shibuya109_logo_gradient_face','shibuya109_logo_metal_return','shibuya109_logo_shibuya_letters']){const mi=prior.j.meshes.findIndex((m:any)=>m.name===name);expect(mi).toBeGreaterThanOrEqual(0);expect(C.removed[mi]).toBeUndefined();expect(C.meshMap[mi]).toBeDefined();}
 });
 it('preserves original materials and exactly the accepted replacement mesh/material set, nodes, transforms and scene membership',()=>{
  expect(live.j.materials.slice(0,prior.j.materials.length)).toEqual(prior.j.materials);expect(live.j.materials.slice(prior.j.materials.length)).toEqual(C.materials);
  expect(live.j.meshes).toHaveLength(retained.size+C.newMeshes.length);
  for(const item of C.newMeshes){expect(live.j.meshes[item.index]).toEqual(item.definition);for(const [i,digest] of Object.entries(item.accessors))expect(sha(raw(live,Number(i)))).toBe(digest);}
  expect(live.j.nodes).toEqual(C.nodes);expect(live.j.scenes).toEqual(C.scenes);expect(live.j.scene??0).toBe(C.scene);
  for(const key of ['extensionsUsed','extensionsRequired','textures','images','samplers','animations','skins'])expect(live.j[key]).toEqual(prior.j[key]);
  for(const n of prior.j.nodes){if(n.mesh===undefined)continue;const target=C.meshMap[n.mesh];if(target===undefined)continue;expect(live.j.nodes.find((v:any)=>v.mesh===target)).toEqual({...n,mesh:target});}
  expect(live.j.meshes.some((m:any)=>['shibuya109_canopy_under','shibuya109_entrance_sign_panel'].includes(m.name))).toBe(false);
 });
 it('keeps accepted counts, original B budgets and finite replacement geometry without new degenerates or opposed normals',()=>{
  let triangles=0,primitives=0,degenerate=0,opposed=0;
  for(const [mi,m] of live.j.meshes.entries())for(const p of m.primitives){primitives++;const ii=values(live,p.indices),v=values(live,p.attributes.POSITION),ns=values(live,p.attributes.NORMAL);triangles+=ii.length/3;expect(v.every(Number.isFinite)&&ns.every(Number.isFinite)).toBe(true);if(retained.has(mi))continue;
   for(let k=0;k<ii.length;k+=3){const a=new Vector3().fromArray(v,3*ii[k]),b=new Vector3().fromArray(v,3*ii[k+1]),c=new Vector3().fromArray(v,3*ii[k+2]),normal=b.sub(a).cross(c.sub(a));if(normal.length()<1e-10)degenerate++;else if(ii.slice(k,k+3).some(i=>normal.dot(new Vector3().fromArray(ns,3*i))< -1e-7))opposed++;}
  }
  expect([triangles,primitives,liveBytes.length]).toEqual([45727,37,2763184]);expect(triangles).toBeLessThanOrEqual(120000);expect(primitives).toBeLessThanOrEqual(40);expect(liveBytes.length).toBeLessThanOrEqual(3000000);expect([degenerate,opposed]).toEqual([0,0]);
 });

 it('has four live fitted-foot contacts with pinned model-ground and only white identity emission',()=>{
  const p=live.j.meshes.find((m:any)=>m.name==='entrance_gold_open_frame').primitives[0],flat=values(live,p.attributes.POSITION);
  const vertices=Array.from({length:flat.length/3},(_,k)=>[flat[3*k],-flat[3*k+2],flat[3*k+1]]);
  function height(x:number,y:number){const zs:number[]=[];for(const [a,b,c] of C.ground.triangles){const den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(Math.abs(den)<1e-9)continue;const u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den,v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;if(Math.min(u,v,1-u-v)>=-1e-7)zs.push(u*a[2]+v*b[2]+(1-u-v)*c[2]);}expect(zs.length).toBeGreaterThan(0);return Math.max(...zs);}
  for(const point of Object.values(C.ground.points) as any[]){const [x,y]=point.xy,foot=vertices.filter(v=>Math.hypot(v[0]-x,v[1]-y)<.24&&Math.abs(v[2]-point.z)<.07);expect(foot.length).toBeGreaterThanOrEqual(16);for(const v of foot)expect(Math.abs(v[2]-height(v[0],v[1]))).toBeLessThan(.00002);}
  expect(C.materials.filter((m:any)=>(m.emissiveFactor??[0,0,0]).some((v:number)=>v!==0)).map((m:any)=>m.name)).toEqual(['entrance_white_identity']);
 });
 it('keeps the live entrance aperture free of original shell and retained-fragment blockers',()=>{
  // Independent tangent-plane rays through actual LIVE triangles; no production builder.
  const triangles:Vector3[][]=[];
  for(const [mi,m] of live.j.meshes.entries()){
   const oldIndex=Object.keys(C.meshMap).find(k=>C.meshMap[k]===mi);
   if(!(oldIndex!==undefined&&+oldIndex>=1&&+oldIndex<=16&&![9,12].includes(+oldIndex))&&!m.name.startsWith('phase2_retained_fragments_'))continue;
   for(const p of m.primitives){const v=values(live,p.attributes.POSITION),ii=values(live,p.indices);for(let k=0;k<ii.length;k+=3)triangles.push(ii.slice(k,k+3).map(i=>new Vector3(v[3*i],-v[3*i+2],v[3*i+1])));}
  }
  const right=new Vector3(.050703,.998716,0),normal=new Vector3(right.y,-right.x,0),center=new Vector3(-129.0380165156,6.9354800658,0),hit=new Vector3();let samples=0,blockers=0;
  for(let i=0;i<15;i++)for(let k=0;k<10;k++){
   const origin=center.clone().addScaledVector(right,-2.62+5.24*i/14).add(normal);origin.z=1.19+2.99*k/9;const ray=new Ray(origin,normal.clone().negate());
   for(const t of triangles){const p=ray.intersectTriangle(t[0],t[1],t[2],false,hit);if(p!==null&&p.distanceTo(origin)>1e-7&&p.distanceTo(origin)<1.999)blockers++;}samples++;
  }
  expect(samples).toBe(150);expect(blockers).toBe(0);
 });
 it('uses actual app loader/classify/emission/look for retained and new materials through day/night/day',async()=>{
  const a=await loaded(priorBytes),b=await loaded(liveBytes);expect(a.ok).toBe(true);expect(b.ok).toBe(true);if(a.ok===false||b.ok===false)throw new Error('Building loader failed');expect(b.layerErrors).toEqual([]);expect(b.stats.meshes).toBe(37);expect(b.stats.triangles).toBe(45727);expect(b.root.position.y).toBe(a.root.position.y);
  const oldStates:any[]=[],newStates:any[]=[];
  for(const mode of ['day','night','day'] as const){for(const [asset,states] of [[a,oldStates],[b,newStates]] as const){const table=asset.emissive[mode];applyEmissive(asset.root,table);applyLook(asset.root,mode,LOOK_DEFAULT,table,{map:null,intensity:1});states.push(rows(asset.root,table));}}
  const drift:string[]=[];
  for(let mode=0;mode<3;mode++)for(const row of newStates[mode]){const old=oldStates[mode].find((r:any)=>r.mesh===row.mesh&&r.material===row.material);if(old)expect(row).toEqual(old);expect([...row.color,...row.emissive].every(Number.isFinite)).toBe(true);}
  for(const first of newStates[0]){const last=newStates[2].find((r:any)=>r.mesh===first.mesh);if(JSON.stringify(first)===JSON.stringify(last))continue;drift.push(first.mesh);const oldFirst=oldStates[0].find((r:any)=>r.mesh===first.mesh),oldLast=oldStates[2].find((r:any)=>r.mesh===first.mesh);expect(oldFirst).toBeDefined();expect(first.emissiveIntensity).toBe(0);expect(last.emissiveIntensity).toBe(0);const changes=(x:any,y:any)=>Object.fromEntries(Object.keys(x).filter(k=>JSON.stringify(x[k])!==JSON.stringify(y[k])).map(k=>[k,[x[k],y[k]]]));expect(Object.keys(changes(first,last))).toEqual(['emissive']);expect(changes(first,last)).toEqual(changes(oldFirst,oldLast));}
  expect(drift.sort()).toEqual(['shibuya109_logo_gradient_face','shibuya109_logo_shibuya_letters']);
  const trim=b.root.getObjectByName('shibuya109_metal_lip') as Mesh;expect((trim.material as MeshStandardMaterial).name).toBe('shibuya109_metal_lip');expect((trim.material as MeshStandardMaterial).color.toArray()).toEqual([.48,.49,.5]);
  const logo=b.root.getObjectByName('shibuya109_logo_gradient_face') as Mesh;expect(logo.geometry.getAttribute('color').count).toBeGreaterThan(0);expect((logo.material as MeshStandardMaterial).vertexColors).toBe(true);
 });
});
