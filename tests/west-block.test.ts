import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';
const base = 'assets/buildings/west-block/';
it('replaces the original C shell exactly once and keeps the PLATEAU source and measured ground datum', () => {
 const source=JSON.parse(readFileSync(base+'source/data/plateau.json','utf8'));
 const context=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 expect(source.id).toBe('way/136690966');
 expect(context.buildings.some((b:{id:string})=>b.id===source.id)).toBe(false);
 expect(context.excluded.filter((b:{id:string})=>b.id===source.id)).toHaveLength(1);
 expect(hints.groundElevationTP).toBe(stats.anchor_tp);
 expect(Math.abs(stats.roof_deviation_vs_plateau_m)).toBeLessThan(.2);
});
it('separates dated signs from geometry and preserves colour textures at night', async () => {
 const io=new NodeIO();
 const root=(await io.read(base+'web/signs-2025-01.glb')).getRoot();
 const names=root.listMaterials().map(m=>m.getName());
 expect(names).toContain('west_sign_hisamitsu');expect(names).toContain('west_sign_taiseido');
 for(const material of root.listMaterials()) {
  expect(material.getBaseColorTexture()).not.toBeNull();
  expect(material.getEmissiveTexture()).not.toBeNull();
 }
 const plain=(await io.read(base+'web/west-block.glb')).getRoot();
 expect(plain.listMaterials().some(m=>m.getName().startsWith('west_sign_'))).toBe(false);
 for(const node of plain.listNodes()) {
  if(!node.getMesh())continue;
  const matrix=new Matrix4().fromArray(node.getWorldMatrix());
  for(const primitive of node.getMesh()!.listPrimitives()) {
   const a=primitive.getAttribute('POSITION')!;
   for(let i=0;i<a.getCount();i++) {
    const p=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(matrix);
    expect([p.x,p.y,p.z].every(Number.isFinite)).toBe(true);
    expect(p.x).toBeGreaterThan(-70);expect(p.x).toBeLessThan(-30);
    expect(p.y).toBeGreaterThan(-.1);expect(p.y).toBeLessThan(50);
   }
  }
 }
});

it('keeps curved billboards within the footprint and visible through the replacement shell', async () => {
 const io=new NodeIO();
 const config=JSON.parse(readFileSync(base+'source/data/facades.json','utf8'));
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 const material=new MeshBasicMaterial({side:DoubleSide});const meshes:Mesh[]=[];
 try {
  for(const file of ['west-block.glb','signs-2025-01.glb']) {
   const root=(await io.read(base+'web/'+file)).getRoot();
   for(const node of root.listNodes()) {
    const world=new Matrix4().fromArray(node.getWorldMatrix());
    for(const prim of node.getMesh()?.listPrimitives()??[]) {
     const pos=prim.getAttribute('POSITION')!;const idx=prim.getIndices();const vertices:number[]=[];
     for(let i=0;i<(idx?.getCount()??pos.getCount());i++) {
      const v=new Vector3().fromArray(pos.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);
      v.y+=hints.groundElevationTP-15;vertices.push(v.x,v.y,v.z);
      if(['west_sign_rakuten','west_sign_dmm','west_sign_taiseido'].includes(prim.getMaterial()!.getName())) expect(v.x).toBeLessThanOrEqual(hints.planBounds[2]+.002);
     }
     const geometry=new BufferGeometry();geometry.setAttribute('position',new Float32BufferAttribute(vertices,3));
     const mesh=new Mesh(geometry,material);mesh.name=prim.getMaterial()!.getName();meshes.push(mesh);
    }
   }
  }
  const cam=JSON.parse(readFileSync('assets/street/core/web/projected.json','utf8')).camera.pos;
  const origin=new Vector3(cam[0],cam[2],-cam[1]);const c=config.corner;
  for(const name of ['rakuten','dmm','taiseido']) {
   const angle=c.center_angle_rad+.02,radius=c.radius_m+.1;
   const target=new Vector3(c.center_m[0]+radius*Math.cos(angle),c.screen_centers_m[name]+hints.groundElevationTP-15,-c.center_m[1]-radius*Math.sin(angle));
   const ray=new Raycaster(origin,target.sub(origin).normalize());
   expect(ray.intersectObjects(meshes,false)[0]?.object.name, name+' hidden by old shell').toBe('west_sign_'+name);
  }
 } finally {for(const mesh of meshes)mesh.geometry.dispose();material.dispose();}
});
