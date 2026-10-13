import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';
const base='assets/buildings/station-north/';
it('replaces the northern facility and JR bridge once while keeping three other C station candidates',()=>{
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 const context=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 for(const p of parts){expect(context.buildings.some((b:{id:string})=>b.id===p.id)).toBe(false);expect(context.excluded.filter((e:{id:string})=>e.id===p.id)).toHaveLength(1);}
 expect(context.buildings.filter((b:{group:string})=>b.group==='station')).toHaveLength(3);
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 expect(stats.platform_deck_tp).toBe(21.29);expect(stats.roof_deviation_vs_plateau_m).toBe(0);expect(stats.north_open_wall_faces).toBeGreaterThan(0);
});
it('retains original roof and complete JR-bridge vertices in the absolute datum',async()=>{
 const root=(await new NodeIO().read(base+'web/station-north.glb')).getRoot(),vertices:Vector3[]=[];
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const a=p.getAttribute('POSITION')!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
  for(let i=0;i<a.getCount();i++)vertices.push(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(matrix));
 }
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 for(const part of parts)for(const s of part.surfaces){
  if(part.kind==='building'&&s.kind!=='RoofSurface')continue;
  for(const p of s.ring)expect(vertices.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.001)).toBe(true);
 }
});
it('opens the north platform above its original deck while retaining southern walls',async()=>{
 const root=(await new NodeIO().read(base+'web/station-north.glb')).getRoot(),meshes:Mesh[]=[];const material=new MeshBasicMaterial({side:DoubleSide});
 try{
  for(const n of root.listNodes())for(const prim of n.getMesh()?.listPrimitives()??[]){
   const world=new Matrix4().fromArray(n.getWorldMatrix()),a=prim.getAttribute('POSITION')!,idx=prim.getIndices(),points:number[]=[];
   for(let i=0;i<(idx?.getCount()??a.getCount());i++){
    const v=new Vector3().fromArray(a.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);expect([v.x,v.y,v.z].every(Number.isFinite)).toBe(true);points.push(v.x,v.y,v.z);
   }
   const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(points,3));const mesh=new Mesh(g,material);mesh.name=prim.getMaterial()!.getName();meshes.push(mesh);
  }
  expect(new Raycaster(new Vector3(64,7.89,30),new Vector3(-1,0,0),0,12).intersectObjects(meshes,false)).toHaveLength(0);
  expect(new Raycaster(new Vector3(85,8,60),new Vector3(-1,0,0),0,30).intersectObjects(meshes,false).length).toBeGreaterThan(0);
  const floor=new Raycaster(new Vector3(62.0467,9,23.8225),new Vector3(0,-1,0)).intersectObjects(meshes,false)[0];
  expect(floor.object.name).toBe('stn_deck');expect(floor.point.y).toBeCloseTo(6.29,2);
 }finally{for(const m of meshes)m.geometry.dispose();material.dispose();}
});
