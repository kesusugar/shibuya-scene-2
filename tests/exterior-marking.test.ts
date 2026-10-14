import {expect,it} from 'vitest';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,Mesh,BufferGeometry,Float32BufferAttribute,MeshBasicMaterial,DoubleSide,Raycaster} from 'three';
for(const id of ['west','middle'])it(`${id} white bars stay on exported roads rather than dropping to zero`,async()=>{
 const root=(await new NodeIO().read(`assets/ground/exterior-${id}/web/exterior-${id}.glb`)).getRoot(),roads:Mesh[]=[],marks:Vector3[]=[],material=new MeshBasicMaterial({side:DoubleSide});
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const pos=p.getAttribute('POSITION')!,idx=p.getIndices()!,world=new Matrix4().fromArray(n.getWorldMatrix());
  if(n.getName()==='ground_marking'){for(let i=0;i<pos.getCount();i+=23)marks.push(new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(world));}
  if(!['ground_road','ground_intersection'].includes(n.getName()))continue;
  const vertices:number[]=[];for(let i=0;i<idx.getCount();i++)vertices.push(...new Vector3().fromArray(pos.getElement(idx.getScalar(i),[])).applyMatrix4(world).toArray());
  const geometry=new BufferGeometry();geometry.setAttribute('position',new Float32BufferAttribute(vertices,3));const mesh=new Mesh(geometry,material);mesh.updateMatrixWorld();roads.push(mesh);
 }
 try{
  expect(marks.length).toBeGreaterThan(0);const ray=new Raycaster();
  for(const p of marks){let matched=false;
   for(const [dx,dz] of [[0,0],[.02,0],[-.02,0],[0,.02],[0,-.02],[.015,.015],[.015,-.015],[-.015,.015],[-.015,-.015]]){
    ray.set(new Vector3(p.x+dx,80,p.z+dz),new Vector3(0,-1,0));const hit=ray.intersectObjects(roads,false)[0];
    if(hit && Math.abs(p.y-hit.point.y-.012)<.025){matched=true;break;}
   }
   expect(matched,`unanchored white bar at ${p.toArray()}`).toBe(true);
  }
 }finally{for(const mesh of roads)mesh.geometry.dispose();material.dispose();}
});
