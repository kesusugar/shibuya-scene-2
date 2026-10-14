import {expect,it} from 'vitest';
import {Group,Mesh,BoxGeometry,MeshStandardMaterial,Raycaster,Vector3,Matrix4,BufferGeometry,Float32BufferAttribute,MeshBasicMaterial,DoubleSide} from 'three';
import {NodeIO} from '@gltf-transform/core';
import {loadTerrain} from '../src/world/terrain';
import {classify} from '../src/world/look';
const fixture=()=>{const g=new Group(),m=new Mesh(new BoxGeometry(),new MeshStandardMaterial({name:'ground_fill_provisional'}));m.name='ground_fill_extension';g.add(m);return g;};
it('isolates a missing supplement and classifies the terrain as provisional fill',async()=>{
 expect((await loadTerrain(async()=>{throw Error('missing')})).ok).toBe(false);
 const r=await loadTerrain(async()=>fixture());expect(r.ok).toBe(true);
 const m=r.root.getObjectByName('ground_fill_extension') as Mesh;expect(classify(m.material as MeshStandardMaterial,m.name)).toBe('fill');
});
it('keeps the exported terrain outside the protected original streets and covers the distant building feet with terrain or added streets',async()=>{
 const io=new NodeIO(),original=(await io.read('assets/ground/core/web/ground_core.glb')).getRoot(),extra=(await io.read('assets/ground/extension/web/extension.glb')).getRoot();
 const material=new MeshBasicMaterial({side:DoubleSide}),meshes:Mesh[]=[];
 const collect=(root:typeof original, includeFill=true)=>{const result:Mesh[]=[];for(const n of root.listNodes())if(/^ground_(road|intersection|sidewalk|fill)/.test(n.getName()) && (includeFill || n.getName()!=='ground_fill'))for(const p of n.getMesh()?.listPrimitives()??[]){
 const a=p.getAttribute('POSITION')!,idx=p.getIndices()!,world=new Matrix4().fromArray(n.getWorldMatrix()),arr:number[]=[];
 for(let i=0;i<idx.getCount();i++)arr.push(...new Vector3().fromArray(a.getElement(idx.getScalar(i),[])).applyMatrix4(world).toArray());
 const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(arr,3));const m=new Mesh(g,material);m.updateMatrixWorld();meshes.push(m);result.push(m);}return result;};
 try{
 const old=collect(original,false),extension=collect(extra),ray=new Raycaster();
 const finished:Mesh[]=[];for(const id of ['west','middle','east'])finished.push(...collect((await io.read(`assets/ground/exterior-${id}/web/exterior-${id}.glb`)).getRoot()));
 const a=extension[0].geometry.getAttribute('position');
 for(let i=0;i<a.count;i+=153){const p=new Vector3();for(let j=0;j<3;j++)p.add(new Vector3().fromBufferAttribute(a,i+j));p.divideScalar(3);ray.set(new Vector3(p.x,60,p.z),new Vector3(0,-1,0));expect(ray.intersectObjects(old,false)).toHaveLength(0);}
 for(const [x,y] of [[157,-165],[-29,-239],[214,-31],[-180,60]]){ray.set(new Vector3(x,60,-y),new Vector3(0,-1,0));expect(ray.intersectObjects([...extension,...finished],false).length).toBeGreaterThan(0);}
 }finally{for(const m of meshes)m.geometry.dispose();material.dispose();}
});
