import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3 } from 'three';
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
