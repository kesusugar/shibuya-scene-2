import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';
const base='assets/buildings/ekimae/';
it('replaces Ekimae C exactly once and anchors the preserved roof to measured ground',()=>{
 const source=JSON.parse(readFileSync(base+'source/data/plateau.json','utf8'));
 const context=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 expect(source.id).toBe('way/60739635');
 expect(context.buildings.some((b:{id:string})=>b.id===source.id)).toBe(false);
 expect(context.excluded.filter((b:{id:string})=>b.id===source.id)).toHaveLength(1);
 expect(hints.groundElevationTP).toBe(stats.anchor_tp);
 expect(stats.frontage_samples.length).toBeGreaterThan(60);
 expect(Math.abs(stats.roof_deviation_vs_plateau_m)).toBeLessThan(.2);
 expect(stats.replaced_corner_faces).toBeGreaterThan(0);
});
it('keeps November ads separately dated with their colour texture at night',async()=>{
 const config=JSON.parse(readFileSync(base+'source/data/facades.json','utf8'));
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 expect(config.photo_date).toBe('2025-11-01');expect(config.license).toBe('CC BY-SA 4.0');
 expect(hints.layers.signs).toBe('signs-2025-11.glb');
 const io=new NodeIO();const signs=(await io.read(base+'web/'+hints.layers.signs)).getRoot();
 expect(signs.listMaterials()).toHaveLength(7);
 for(const m of signs.listMaterials()){expect(m.getBaseColorTexture()).not.toBeNull();expect(m.getEmissiveTexture()).not.toBeNull();}
 const plain=(await io.read(base+'web/ekimae.glb')).getRoot();
 expect(plain.listMaterials().some(m=>m.getName().startsWith('ek_sign_'))).toBe(false);
});
it('renders roof and restaurant signs in front of the replacement shell within the building bounds',async()=>{
 const io=new NodeIO(),meshes:Mesh[]=[];const material=new MeshBasicMaterial({side:DoubleSide});
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 const config=JSON.parse(readFileSync(base+'source/data/facades.json','utf8'));
 try {
  for(const file of ['ekimae.glb','signs-2025-11.glb']){
   const root=(await io.read(base+'web/'+file)).getRoot();
   for(const node of root.listNodes())for(const prim of node.getMesh()?.listPrimitives()??[]){
    const matrix=new Matrix4().fromArray(node.getWorldMatrix()),pos=prim.getAttribute('POSITION')!,idx=prim.getIndices(),vertices:number[]=[];
    for(let i=0;i<(idx?.getCount()??pos.getCount());i++){
     const p=new Vector3().fromArray(pos.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(matrix);
     expect([p.x,p.y,p.z].every(Number.isFinite)).toBe(true);
     expect(p.x).toBeGreaterThan(hints.planBounds[0]-1.2);expect(p.x).toBeLessThan(hints.planBounds[2]+1.2);
     p.y+=hints.groundElevationTP-15;vertices.push(p.x,p.y,p.z);
    }
    const geometry=new BufferGeometry();geometry.setAttribute('position',new Float32BufferAttribute(vertices,3));const mesh=new Mesh(geometry,material);mesh.name=prim.getMaterial()!.getName();meshes.push(mesh);
   }
  }
  const c=JSON.parse(readFileSync('assets/street/core/web/projected.json','utf8')).camera.pos,origin=new Vector3(c[0],c[2],-c[1]);
  for(const [name,height] of [['samsung',config.rooftop.center_height_m],['gusto',22.75]] as [string,number][]){
   const tangent=new Vector3(-6.687,0,33.648).normalize(),normal=new Vector3(tangent.z,0,-tangent.x);
   const target=new Vector3(-38.316,height+hints.groundElevationTP-15,20.562).addScaledVector(tangent,6.5).addScaledVector(normal,name==='samsung'?.25:.29);
   expect(new Raycaster(origin,target.sub(origin).normalize()).intersectObjects(meshes,false)[0]?.object.name).toBe('ek_sign_'+name);
  }
 } finally {for(const mesh of meshes)mesh.geometry.dispose();material.dispose();}
});
