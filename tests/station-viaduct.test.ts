import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,BufferGeometry,Float32BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Raycaster} from 'three';
const base='assets/buildings/station-west-viaduct/';
it('replaces the source block once and keeps one C station candidate',()=>{
 const id=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'))[0].id;
 const c=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 expect(c.buildings.some((b:{id:string})=>b.id===id)).toBe(false);expect(c.excluded.filter((b:{id:string})=>b.id===id)).toHaveLength(1);
 expect(c.buildings.filter((b:{group:string})=>b.group==='station')).toHaveLength(1);
 expect(JSON.parse(readFileSync(base+'web/viewer.json','utf8')).groundElevationTP).toBe(15);
});
it('preserves the original top and uses a transparent non-glowing safety-net approximation',async()=>{
 const root=(await new NodeIO().read(base+'web/station-west-viaduct.glb')).getRoot(),vertices:Vector3[]=[];
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  if(p.getMaterial()!.getName()!=='wv_top')continue;
  const a=p.getAttribute('POSITION')!,world=new Matrix4().fromArray(n.getWorldMatrix());
  for(let i=0;i<a.getCount();i++)vertices.push(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(world));
 }
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 for(const s of parts[0].surfaces.filter((s:{kind:string})=>s.kind==='RoofSurface'))for(const p of s.ring)
  expect(vertices.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.001)).toBe(true);
 const net=root.listMaterials().find(m=>m.getName()==='wv_mesh')!;
 expect(net.getAlphaMode()).toBe('BLEND');expect(net.getBaseColorFactor()[3]).toBeLessThan(.5);
 expect(root.listMaterials().some(m=>/glass|window/i.test(m.getName()))).toBe(false);
 for(const mode of ['day','night'])expect(JSON.parse(readFileSync(base+`web/emissive_${mode}.json`,'utf8'))).toEqual({});
});
it('opens the lower span while preserving piers and their recorded absolute foot heights',async()=>{
 const root=(await new NodeIO().read(base+'web/station-west-viaduct.glb')).getRoot(),meshes:Mesh[]=[],material=new MeshBasicMaterial({side:DoubleSide});let lowest=Infinity;
 try{
  for(const n of root.listNodes())for(const prim of n.getMesh()?.listPrimitives()??[]){
   const a=prim.getAttribute('POSITION')!,idx=prim.getIndices(),world=new Matrix4().fromArray(n.getWorldMatrix()),pts:number[]=[];
   for(let i=0;i<(idx?.getCount()??a.getCount());i++){
    const p=new Vector3().fromArray(a.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);expect([p.x,p.y,p.z].every(Number.isFinite)).toBe(true);lowest=Math.min(lowest,p.y);pts.push(p.x,p.y,p.z);
   }
   const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(pts,3));const m=new Mesh(g,material);m.name=prim.getMaterial()!.getName();meshes.push(m);
  }
  const t=new Vector3(59.539,0,-9.640).normalize(),normal=new Vector3(t.z,0,-t.x);
  const ray=(u:number)=>new Raycaster(new Vector3(4.623,4,89.839).addScaledVector(t,u).addScaledVector(normal,.5),normal.clone().negate(),0,10).intersectObjects(meshes,false);
  expect([5,13,21,29,37,45,53].filter(u=>ray(u).length===0).length).toBeGreaterThanOrEqual(5);
  expect(ray(1.5).some(h=>h.object.name==='wv_steel')).toBe(true);
  const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
  expect(lowest+15).toBeCloseTo(Math.min(...stats.ground_samples.map((s:{tp:number})=>s.tp)),3);
  expect(stats.ground_samples).toHaveLength(8);
 }finally{for(const m of meshes)m.geometry.dispose();material.dispose();}
});
