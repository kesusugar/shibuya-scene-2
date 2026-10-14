import {expect,it} from 'vitest';
import {readFileSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3} from 'three';
import {LEVEL_BUDGET} from '../src/perf/budget';
const base='assets/buildings/center244/';
const json=(p:string)=>JSON.parse(readFileSync(base+p,'utf8'));
it('Center244 preserves exact raw source, low roofs and top while explicitly reinterpreting billboard envelope',async()=>{
 const hash=createHash('sha256').update(readFileSync(base+'source/data/plateau.json')).digest('hex');
 expect(hash).toBe('3df9205722f35b952183fb20bae33fb67e6c30b0f273592f5ed5a753ca38dc3a');
 const doc=await new NodeIO().read(base+'web/center244.glb');const roof:Vector3[]=[];const all:Vector3[]=[];
 for(const n of doc.getRoot().listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const a=p.getAttribute('POSITION')!;const m=new Matrix4().fromArray(n.getWorldMatrix());
  for(let i=0;i<a.getCount();i++){const v=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m);all.push(v);if(p.getMaterial()!.getName()==='c244_roof')roof.push(v);}
 }
 const source=json('source/data/plateau.json');
 for(const s of source.surfaces.filter((s:{kind:string,ring:number[][]})=>s.kind==='RoofSurface'&&s.ring.every(p=>p[2]<=21.635)))for(const p of s.ring)
  expect(roof.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.002)).toBe(true);
 expect(Math.max(...all.map(v=>v.y))).toBeCloseTo(34.843,3);
 const s=json('source/data/stats.json');expect(s.roof_translation_m).toBe(0);expect(s.upper_reinterpreted_indices).toEqual([1,3,4,5,7,14,17,25,26,27,29,32,33]);
 expect(s.upper_original_visible_mesh_preserved).toBe(false);expect(s.upper_original_hidden_provenance_preserved).toBe(true);
});
it('Center244 keeps date-specific imagery out of base and unregistered in unconditional loader',async()=>{
 const io=new NodeIO();const b=(await io.read(base+'web/center244.glb')).getRoot();const era=(await io.read(base+'web/signs-2025-01.glb')).getRoot();
 expect(b.listMaterials().every(m=>m.getBaseColorTexture()===null)).toBe(true);
 expect(era.listMaterials().every(m=>m.getName().includes('2025_01'))).toBe(true);
 expect(era.listTextures()).toHaveLength(2);expect(json('web/viewer.json').layers).toBeUndefined();expect(json('web/viewer.json').groundElevationTP).toBe(15);
});
it('Center244 combined base+January asset stays within unchanged B budgets',async()=>{
 let triangles=0,primitives=0,bytes=0;
 for(const name of ['center244.glb','signs-2025-01.glb']){
  bytes+=statSync(base+'web/'+name).size;const root=(await new NodeIO().read(base+'web/'+name)).getRoot();
  for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){primitives++;triangles+=(p.getIndices()?.getCount()??p.getAttribute('POSITION')!.getCount())/3;}
 }
 expect(triangles).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);expect(primitives).toBeLessThanOrEqual(LEVEL_BUDGET.B.primitives);expect(bytes).toBeLessThanOrEqual(LEVEL_BUDGET.B.bytes);
 expect(json('source/data/stats.json').triangles).toBe(triangles);
});
