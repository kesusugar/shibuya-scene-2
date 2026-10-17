import {it,expect} from 'vitest';
import {NodeIO, type Node} from '@gltf-transform/core';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Group,Mesh,BufferGeometry,BufferAttribute,MeshBasicMaterial,Matrix4,Vector3} from 'three';
import {loadSurround} from '../src/world/surround';
const base='assets/street/hachiko-surround/',io=new NodeIO();
const sha=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
function object(n:Node):Group {
 const g=new Group();g.name=n.getName();g.applyMatrix4(new Matrix4().fromArray(n.getMatrix()));
 for(const p of n.getMesh()?.listPrimitives()??[]){
  const geo=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));
  geo.setIndex(new BufferAttribute(p.getIndices()!.getArray()!,1));g.add(new Mesh(geo,new MeshBasicMaterial()));
 }
 for(const child of n.listChildren())g.add(object(child));return g;
}
it('installs the delivered world shrubs once and grounds both seating roots in the independent equipment frame',async()=>{
 const result=await loadSurround(async(url)=>{
  const doc=await io.read(base+'web/'+url.split('/').pop()),g=new Group();
  for(const n of doc.getRoot().listScenes()[0].listChildren())g.add(object(n));return g;
 });expect(result.ok).toBe(true);expect(result.stats.triangles).toBe(26552);
 expect(result.root.children).toHaveLength(3);expect(result.root.position.toArray()).toEqual([0,0,0]);
 expect(result.root.children[1].matrix.toArray()).toEqual(new Matrix4().toArray());
 const equipment=result.root.getObjectByName('surround:seating')!;
 expect(equipment.rotation.y).toBeCloseTo(35*Math.PI/180,12);
 const mounting=JSON.parse(readFileSync(base+'source/deliveries/hachiko_seating_paving_v002/docs/MOUNTING.json','utf8'));
 expect(equipment.position.toArray()).toEqual(mounting.frame.threejs_parent_translation_m);
 result.root.updateMatrixWorld(true);
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 for(const [i,side] of ['left','right'].entries()){
  const node=equipment.getObjectByName(`current_${side}_statue_local_origin`)!;
  expect(node.position.y).toBe(mounting.child_anchors[i].threejs_local_position_y_m);
  const record=stats.items.find((s:{id:string})=>s.id===side);
  expect(record.contact_samples).toHaveLength(9);
  for(const sample of record.contact_samples){
   const p=node.localToWorld(new Vector3(sample.local[0],0,-sample.local[1]));
   expect(p.x).toBeCloseTo(sample.xy[0],7);expect(-p.z).toBeCloseTo(sample.xy[1],7);
   expect(p.y-sample.ground_z).toBeLessThanOrEqual(.00001);expect(p.y-sample.ground_z).toBeGreaterThan(-.041);
  }
 }
 // Same ground hash as the delivered 9-point contact basis, no re-fit needed.
 expect(sha('assets/ground/core/web/ground_core.glb')).toBe('37755dd24d3fe78418b3133210a6dc05ebe2c3c2f615b5a8bd22a4db6279dd32');
 expect(sha(base+'web/shrubs.glb')).toBe(sha(base+'source/deliveries/hachiko_low_shrubs_v002/models/hachiko_low_shrubs_only_v002.glb'));
 const roots=JSON.parse(readFileSync(base+'source/deliveries/hachiko_low_shrubs_v002/models/shrub_roots.json','utf8'));expect(roots).toHaveLength(6);
});
it('changes only seating texture resolution, keeping every geometry attribute, node transform and material mode',async()=>{
 const a=(await io.read(base+'source/deliveries/hachiko_seating_paving_v002/web/current_pair.glb')).getRoot();
 const b=(await io.read(base+'web/seating.glb')).getRoot();
 for(const [i,n] of a.listNodes().entries())expect(b.listNodes()[i].getMatrix()).toEqual(n.getMatrix());
 for(const [i,mesh] of a.listMeshes().entries())for(const [j,p] of mesh.listPrimitives().entries()){
  const other=b.listMeshes()[i].listPrimitives()[j];
  for(const semantic of p.listSemantics()){
   const x=p.getAttribute(semantic)!.getArray()!,y=other.getAttribute(semantic)!.getArray()!;
   expect(Buffer.from(x.buffer,x.byteOffset,x.byteLength).equals(Buffer.from(y.buffer,y.byteOffset,y.byteLength))).toBe(true);
  }
  expect(other.getMaterial()!.getAlphaMode()).toBe(p.getMaterial()!.getAlphaMode());
 }
});
