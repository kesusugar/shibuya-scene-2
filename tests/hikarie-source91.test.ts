import { expect,it } from 'vitest';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Vector3,Mesh,MeshStandardMaterial} from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {classify,applyLook,LOOK_DEFAULT} from '../src/world/look';
import {applyEmissive,type EmissiveTable} from '../src/world/buildings';
import {isSource91Removal,isSource91Overlay} from './helpers/hikarie-source91-contract';
const base='assets/buildings/hikarie/';
const sha=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
function load(path:string){
 const raw=readFileSync(path),n=raw.readUInt32LE(12),j=JSON.parse(raw.subarray(20,20+n).toString()),bin=raw.subarray(28+n);
 const widths:Record<number,number>={5121:1,5123:2,5125:4,5126:4};const comps:Record<string,number>={SCALAR:1,VEC2:2,VEC3:3,VEC4:4};
 const bytes=(id:number)=>{const a=j.accessors[id],v=j.bufferViews[a.bufferView],w=widths[a.componentType]*comps[a.type];return Buffer.concat(Array.from({length:a.count},(_,i)=>{const o=(v.byteOffset??0)+(a.byteOffset??0)+i*(v.byteStride??w);return bin.subarray(o,o+w);}));};
 const values=(id:number)=>{const a=j.accessors[id],b=bytes(id),w=widths[a.componentType];return Array.from({length:b.length/w},(_,i)=>a.componentType===5126?b.readFloatLE(i*w):a.componentType===5125?b.readUInt32LE(i*w):a.componentType===5123?b.readUInt16LE(i*w):b.readUInt8(i));};
 return{raw,j,bin,bytes,values};
}
const prior=load(base+'source/facade91-v1/baseline/hikarie.glb'),live=load(base+'web/hikarie.glb');
it('pins source91 input and live artifact and original source geography',()=>{
 expect(sha(prior.raw)).toBe('14cb88b7d3870512c23a750e7b9f701e85dc184cc1d473954725b6c138a0749d');
 expect(sha(live.raw)).toBe('2f4e95126c0d126c8db2d7d8aad4a54d5d0010ba7af0734b357a939077a87721');
 expect(sha(readFileSync(base+'source/data/plateau.json'))).toBe('49cafd4ce7ded54115267ff5cab3847e0b72d0bfd181fea8f582b8a7c6eb35c2');
});
it('removes exactly906 independent source91 overlay triangles and preserves204 with every off-target index and attribute',()=>{
 expect(live.bin.subarray(0,prior.bin.length).equals(prior.bin)).toBe(true);
 const expected=structuredClone(prior.j);let removed=0,retained=0,total=0,degBefore=0,degAfter=0;
 prior.j.meshes.forEach((m:any,mi:number)=>m.primitives.forEach((p:any,pi:number)=>{
  const q=live.j.meshes[mi].primitives[pi];expect({...q,indices:p.indices}).toEqual(p);
  for(const [semantic,id] of Object.entries(p.attributes)){expect(live.bytes(q.attributes[semantic]).equals(prior.bytes(id as number))).toBe(true);}
  const xyz=prior.values(p.attributes.POSITION),old=prior.values(p.indices),got=live.values(q.indices),keep:number[]=[];
  for(let i=0;i<old.length;i+=3){const ids=old.slice(i,i+3),pts=ids.map(id=>new Vector3(...xyz.slice(id*3,id*3+3) as [number,number,number]));
   // Roof and original shell are never eligible even if coplanar.
   const eligible=!['hikarie_wall','hikarie_roof'].includes(prior.j.materials[p.material].name);
   const remove=eligible&&isSource91Removal(pts);if(remove)removed++;else{keep.push(...ids);if(eligible&&isSource91Overlay(pts))retained++;}
   const deg=pts[1].clone().sub(pts[0]).cross(pts[2].clone().sub(pts[0])).length()<1e-9;if(deg){degBefore++;if(!remove)degAfter++;}
  }
  expect(got,`${m.name} retained index order`).toEqual(keep);total+=got.length/3;expected.meshes[mi].primitives[pi].indices=q.indices;
 }));
 expect(removed).toBe(906);expect(retained).toBe(204);expect(total).toBe(30562);expect(degBefore).toBe(2);expect(degAfter).toBe(2);
 for(const key of ['accessors','bufferViews']){expect(live.j[key].slice(0,prior.j[key].length)).toEqual(prior.j[key]);expected[key]=live.j[key];}
 expected.buffers=live.j.buffers;expect(live.j).toEqual(expected);
});
it('retains exact live roof/shell, materials, transforms and scene graph within unchanged B budget',()=>{
 for(const name of ['hikarie_roof','hikarie_wall']){const a=prior.j.meshes.find((m:any)=>m.name===name),b=live.j.meshes.find((m:any)=>m.name===name);expect(b).toEqual(a);for(const p of a.primitives){expect(live.bytes(p.indices).equals(prior.bytes(p.indices))).toBe(true);}}
 for(const key of ['materials','nodes','scenes','scene'])expect(live.j[key]).toEqual(prior.j[key]);
 expect(live.j.textures??[]).toHaveLength(0);let triangles=0,primitives=0;
 for(const m of live.j.meshes)for(const p of m.primitives){primitives++;triangles+=live.j.accessors[p.indices].count/3;for(const id of Object.values(p.attributes))expect(live.values(id as number).every(Number.isFinite)).toBe(true);}
 expect(primitives).toBe(15);expect(triangles).toBe(30562);expect(live.raw.length).toBe(2349752);expect(primitives).toBeLessThanOrEqual(40);expect(triangles).toBeLessThanOrEqual(120000);expect(live.raw.length).toBeLessThanOrEqual(3000000);
});
it('loads live geometry with Three and preserves every retained material through day/night/day',async()=>{
 const parse=(raw:Buffer)=>new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength) as ArrayBuffer,'');
 const a=await parse(prior.raw),b=await parse(live.raw);
 const state=(m:MeshStandardMaterial)=>({name:m.name,color:m.color.toArray(),emissive:m.emissive.toArray(),emissiveIntensity:m.emissiveIntensity,roughness:m.roughness,metalness:m.metalness,transparent:m.transparent,opacity:m.opacity,side:m.side,vertexColors:m.vertexColors,envMapIntensity:m.envMapIntensity});
 let compared=0;
 for(const mode of ['day','night','day'] as const){const table=JSON.parse(readFileSync(base+`web/emissive_${mode}.json`,'utf8')) as EmissiveTable;
  for(const g of [a,b]){applyEmissive(g.scene,table);applyLook(g.scene,mode,LOOK_DEFAULT,table,{map:null,intensity:1});}
  b.scene.traverse(o=>{if(!(o instanceof Mesh))return;const old=a.scene.getObjectByName(o.name) as Mesh;expect(old).toBeDefined();const m=o.material as MeshStandardMaterial,n=old.material as MeshStandardMaterial;expect(state(m)).toEqual(state(n));expect(classify(m,o.name,table)).toBe(classify(n,old.name,table));for(const key of Object.keys(old.geometry.attributes)){expect(o.geometry.getAttribute(key).array).toEqual(old.geometry.getAttribute(key).array);}compared++;});
 }
 expect(compared).toBe(45);
});

