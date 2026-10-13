import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Group,Mesh,BoxGeometry,MeshStandardMaterial,Matrix4,Vector3} from 'three';
import {loadFacilities} from '../src/world/facilities';
const base='assets/street/plaza-facilities/',json=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
it('isolates failed loading and requires the actual facility mesh',async()=>{
 expect((await loadFacilities(async()=>{throw Error('missing')})).ok).toBe(false);
 expect((await loadFacilities(async()=>new Group())).ok).toBe(false);
 const g=new Group(),m=new Mesh(new BoxGeometry(),new MeshStandardMaterial());m.name='street_plaza_facilities_housing';g.add(m);
 expect((await loadFacilities(async()=>g)).ok).toBe(true);
});
it('uses 2025 OSM small footprints and recorded Core contacts instead of a default 9m tower',async()=>{
 const d=json(base+'source/data/layout.json'),s=json(base+'source/data/stats.json');
 expect(d.query_date).toBe('2025-10-31T23:59:59Z');expect(d.items).toHaveLength(2);
 for(const item of s.items){expect(item.height_estimated_m).toBeLessThanOrEqual(3.03);expect(item.ground_samples.every((p:{tp:number})=>Number.isFinite(p.tp))).toBe(true);expect(item.top_tp_m-item.base_tp_m).toBeCloseTo(item.height_estimated_m,5);}
 const root=(await new NodeIO().read(base+'web/plaza-facilities.glb')).getRoot();let low=Infinity,high=-Infinity;
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){expect(p.getMaterial()!.getBaseColorTexture()).toBeNull();const a=p.getAttribute('POSITION')!,world=new Matrix4().fromArray(n.getWorldMatrix());for(let i=0;i<a.getCount();i++){const v=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(world);expect([v.x,v.y,v.z].every(Number.isFinite)).toBe(true);low=Math.min(low,v.y+15);high=Math.max(high,v.y+15);}}
 expect(low).toBeCloseTo(Math.min(...s.items.map((p:{base_tp_m:number})=>p.base_tp_m)),3);
 expect(high).toBeCloseTo(Math.max(...s.items.map((p:{top_tp_m:number})=>p.top_tp_m)),3);
});
