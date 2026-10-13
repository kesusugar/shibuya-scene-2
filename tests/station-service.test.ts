import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,BufferGeometry,Float32BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Raycaster} from 'three';
const base='assets/buildings/station-service/';
it('replaces the facility once and retains three other C station candidates',()=>{
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 const context=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 const id=parts[0].id;expect(context.buildings.some((b:{id:string})=>b.id===id)).toBe(false);
 expect(context.excluded.filter((b:{id:string})=>b.id===id)).toHaveLength(1);
 expect(context.buildings.filter((b:{group:string})=>b.group==='station')).toHaveLength(3);
 expect(JSON.parse(readFileSync(base+'web/viewer.json','utf8')).groundElevationTP).toBe(15);
});
it('retains every original shell/roof vertex without generic glass or glowing windows',async()=>{
 const root=(await new NodeIO().read(base+'web/station-service.glb')).getRoot(),vertices:Vector3[]=[];
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const a=p.getAttribute('POSITION')!,world=new Matrix4().fromArray(n.getWorldMatrix());
  for(let i=0;i<a.getCount();i++){const v=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(world);expect([v.x,v.y,v.z].every(Number.isFinite)).toBe(true);vertices.push(v);}
 }
 for(const b of JSON.parse(readFileSync(base+'source/data/parts.json','utf8')))for(const s of b.surfaces)for(const p of s.ring)
  expect(vertices.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.001)).toBe(true);
 expect(Math.max(...vertices.map(v=>v.y))).toBeLessThanOrEqual(13.101);
 expect(root.listMaterials().some(m=>/glass|window/i.test(m.getName()))).toBe(false);
 for(const time of ['day','night'])expect(JSON.parse(readFileSync(base+`web/emissive_${time}.json`,'utf8'))).toEqual({});
});
it('closes the gap below the original base at locally measured lower ground',async()=>{
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 expect(stats.ground_samples.length).toBeGreaterThan(40);expect(stats.roof_deviation_vs_plateau_m).toBe(0);
 const sample=stats.ground_samples.filter((p:{tp:number})=>p.tp<15.35&&p.tp>15.0).find((p:{x:number,y:number})=>p.y>-62&&p.x>32&&p.x<40);
 expect(sample).toBeDefined();
 const root=(await new NodeIO().read(base+'web/station-service.glb')).getRoot(),meshes:Mesh[]=[],material=new MeshBasicMaterial({side:DoubleSide});
 try{
  for(const n of root.listNodes())for(const prim of n.getMesh()?.listPrimitives()??[]){
   const a=prim.getAttribute('POSITION')!,idx=prim.getIndices(),world=new Matrix4().fromArray(n.getWorldMatrix()),pts:number[]=[];
   for(let i=0;i<(idx?.getCount()??a.getCount());i++){
    const p=new Vector3().fromArray(a.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);pts.push(p.x,p.y,p.z);
   }
   const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(pts,3));const m=new Mesh(g,material);m.name=prim.getMaterial()!.getName();meshes.push(m);
  }
  const normal=new Vector3(-2.709,0,-18.019).normalize();
  const origin=new Vector3(sample.x,(sample.tp+15.439)/2-15,-sample.y).addScaledVector(normal,.25);
  const hit=new Raycaster(origin,normal.clone().negate(),0,.8).intersectObjects(meshes,false)[0];
  expect(hit?.object.name).toBe('ss_plinth');
 }finally{for(const m of meshes)m.geometry.dispose();material.dispose();}
});
