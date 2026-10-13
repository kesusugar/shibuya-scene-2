import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';
const base='assets/buildings/station-concourse/';
it('replaces both solid wrappers exactly once without certifying the five station buildings',()=>{
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 const context=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 for(const part of parts){expect(context.buildings.some((b:{id:string})=>b.id===part.id)).toBe(false);expect(context.excluded.filter((e:{id:string})=>e.id===part.id)).toHaveLength(1);}
 expect(context.buildings.filter((b:{group:string})=>b.group==='station')).toHaveLength(5);
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 expect(hints.groundElevationTP).toBe(15);
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 expect(stats.ground_samples.length).toBeGreaterThan(20);
 expect(stats.roof_deviation_vs_plateau_m).toBe(0);
});
it('preserves all original roof vertices in the common absolute datum',async()=>{
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 const io=new NodeIO(),root=(await io.read(base+'web/station-concourse.glb')).getRoot();
 const vertices:Vector3[]=[];
 for(const node of root.listNodes())for(const p of node.getMesh()?.listPrimitives()??[]){
  if(p.getMaterial()!.getName()!=='sc_roof')continue;
  const a=p.getAttribute('POSITION')!,world=new Matrix4().fromArray(node.getWorldMatrix());
  for(let i=0;i<a.getCount();i++)vertices.push(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(world));
 }
 for(const s of parts.find((p:{kind:string})=>p.kind==='building').surfaces.filter((s:{kind:string})=>s.kind==='RoofSurface'))for(const p of s.ring){
  const expected=new Vector3(p[0],p[2],-p[1]);expect(vertices.some(v=>v.distanceTo(expected)<.001)).toBe(true);
 }
});
it('opens the east bay while retaining the western ground-level solid',async()=>{
 const io=new NodeIO(),root=(await io.read(base+'web/station-concourse.glb')).getRoot(),meshes:Mesh[]=[];
 const material=new MeshBasicMaterial({side:DoubleSide});
 try {
  for(const node of root.listNodes())for(const prim of node.getMesh()?.listPrimitives()??[]){
   const world=new Matrix4().fromArray(node.getWorldMatrix()),a=prim.getAttribute('POSITION')!,idx=prim.getIndices(),pts:number[]=[];
   for(let i=0;i<(idx?.getCount()??a.getCount());i++){const p=new Vector3().fromArray(a.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);expect([p.x,p.y,p.z].every(Number.isFinite)).toBe(true);pts.push(p.x,p.y,p.z);}
   const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(pts,3));const mesh=new Mesh(g,material);mesh.name=prim.getMaterial()!.getName();meshes.push(mesh);
  }
  const hits=(x:number)=>new Raycaster(new Vector3(x,2.5,62),new Vector3(0,0,1),0,30).intersectObjects(meshes,false);
  expect([-11,-7,-3,1].filter(x=>hits(x).length===0).length).toBeGreaterThanOrEqual(2);
  expect(hits(-25).length).toBeGreaterThan(0);
 } finally {for(const m of meshes)m.geometry.dispose();material.dispose();}
});
