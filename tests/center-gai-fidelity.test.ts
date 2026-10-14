import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { NodeIO } from '@gltf-transform/core';
import { Vector3, Matrix4, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';
const base='assets/buildings/center-gai-gate/';
const json=(p:string)=>JSON.parse(readFileSync(base+p,'utf8'));
async function load() {
 const root=(await new NodeIO().read(base+'web/center-gai-gate.glb')).getRoot(), meshes:Mesh[]=[];
 for(const n of root.listNodes()) for(const p of n.getMesh()?.listPrimitives()??[]) {
  const a=p.getAttribute('POSITION')!, m=new Matrix4().fromArray(n.getWorldMatrix()), xyz:number[]=[];
  for(let i=0;i<a.getCount();i++)xyz.push(...new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m).toArray());
  const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(xyz,3));g.setIndex(Array.from(p.getIndices()!.getArray()!));
  const mesh=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));mesh.name=p.getMaterial()!.getName();meshes.push(mesh);
 } return {root,meshes};
}
it('preserves the January campaign bytes, source identity, foot samples and datum',()=>{
 expect(createHash('sha256').update(readFileSync(base+'web/signs-2025-01.glb')).digest('hex')).toBe('e3d61300241cfc5cf3692739f1a33d994d5abc05f64b703536ec35495852d3ec');
 expect(json('source/data/layout.json').foot_points).toEqual([[-31.2,36],[-23,35]]);
 expect(json('source/data/layout.json').source_id).toBe('photo/center-gai-entrance-gate');
 expect(json('source/data/stats.json').feet).toEqual(json('source/data/recorded_ground.json').feet);
 expect(json('web/viewer.json').groundElevationTP).toBe(15);
});
it('records actual mesh crest and keeps a modest geometry budget',async()=>{
 const {meshes}=await load();let top=-Infinity,triangles=0;
 for(const m of meshes){const p=m.geometry.getAttribute('position');for(let i=0;i<p.count;i++)top=Math.max(top,p.getY(i));triangles+=m.geometry.index!.count/3;}
 expect(json('source/data/stats.json').top_local_m).toBeCloseTo(top,5);expect(top).toBeLessThan(6.55);expect(top).toBeGreaterThan(6.4);
 expect(triangles).toBe(json('source/data/stats.json').triangles);expect(triangles).toBeLessThan(3000);expect(meshes.length).toBeLessThanOrEqual(8);
});
it('retains original support bottoms, collidable shafts and open walking passage',async()=>{
 const {meshes}=await load(),feet=json('source/data/stats.json').feet;
 for(const f of feet){const ps:number[]=[];for(const m of meshes.filter(x=>x.name==='gate_base')){const p=m.geometry.getAttribute('position');for(let i=0;i<p.count;i++)if(Math.hypot(p.getX(i)-f.xy[0],p.getZ(i)+f.xy[1])<.4)ps.push(p.getY(i));}expect(Math.min(...ps)).toBeCloseTo(f.min_tp-15-.025,5);}
 const a=new Vector3(-31.2,1.9,-36),b=new Vector3(-23,1.9,-35),t=b.clone().sub(a).normalize(),n=new Vector3(-t.z,0,t.x),c=a.clone().add(b).multiplyScalar(.5);
 expect(new Raycaster(c.clone().addScaledVector(n,3),n.clone().negate(),0,6).intersectObjects(meshes)).toHaveLength(0);
 expect(new Raycaster(a.clone().addScaledVector(n,1),n.clone().negate(),0,2).intersectObjects(meshes)[0].object.name).toBe('gate_crook');
 expect(json('source/data/stats.json').min_clear_height_m).toBeGreaterThan(4);
});
it('keeps permanent architecture separate from the optional campaign material',async()=>{
 const {root}=await load();expect(root.listMaterials().some(m=>m.getName()==='gate_name')).toBe(true);
 expect(root.listMaterials().some(m=>m.getName()==='gate_sign_banner')).toBe(false);
 const sign=(await new NodeIO().read(base+'web/signs-2025-01.glb')).getRoot();expect(sign.listMaterials().map(m=>m.getName())).toEqual(['gate_sign_banner']);
});
