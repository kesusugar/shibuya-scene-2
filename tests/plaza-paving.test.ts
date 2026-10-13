import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3 } from 'three';
import { classify } from '../src/world/look';
import { MeshStandardMaterial } from 'three';

const layout = JSON.parse(readFileSync('assets/ground/core/source/data/plaza_paving_layout.json', 'utf8'));
const contains = (x: number,y: number) => {
  let inside = false;
  for (let i=0; i<layout.polygon_xy_m.length; i++) {
    const [x1,y1] = layout.polygon_xy_m[i], [x2,y2] = layout.polygon_xy_m[(i+layout.polygon_xy_m.length-1)%layout.polygon_xy_m.length];
    if ((y1>y)!==(y2>y) && x<(x2-x1)*(y-y1)/(y2-y1)+x1) inside = !inside;
  }
  return inside;
};

it('exports plaza paving as a separate repeating sidewalk material, without touching roads or fill', async () => {
  const root = (await new NodeIO().read('assets/ground/core/web/ground_core.glb')).getRoot();
  const plaza = root.listMaterials().find(m => m.getName() === 'ground_sidewalk_plaza_pavers')!;
  expect(plaza.getBaseColorTexture()).not.toBeNull();
  expect(plaza.getBaseColorFactor()).toEqual([.30,.28,.25,1]);
  expect(plaza.getBaseColorTextureInfo()!.getWrapS()).toBe(10497);
  expect(plaza.getBaseColorTextureInfo()!.getWrapT()).toBe(10497);
  expect(classify(new MeshStandardMaterial({name: plaza.getName()}), 'ground_sidewalk')).toBe('sidewalk');
  for (const node of root.listNodes()) for (const prim of node.getMesh()?.listPrimitives() ?? []) {
    if (node.getName() !== 'ground_sidewalk') expect(prim.getMaterial()!.getBaseColorTexture()).toBeNull();
  }
});

it('limits plaza triangles to its polygon and keeps paving at the configured metre scale', async () => {
  const root = (await new NodeIO().read('assets/ground/core/web/ground_core.glb')).getRoot();
  const a=layout.yaw_deg*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
  const [px,py]=layout.tile_size_m.map((n: number,i: number)=>n*layout.atlas_tiles[i]);
  const [ox,oy]=layout.origin_xy_m;
  let triangles=0;
  for (const node of root.listNodes()) for (const prim of node.getMesh()?.listPrimitives() ?? []) {
    if (prim.getMaterial()!.getName() !== 'ground_sidewalk_plaza_pavers') continue;
    const matrix=new Matrix4().fromArray(node.getWorldMatrix()),pos=prim.getAttribute('POSITION')!,uv=prim.getAttribute('TEXCOORD_0')!,idx=prim.getIndices()!;
    for (let i=0;i<pos.getCount();i+=Math.max(1,Math.floor(pos.getCount()/500))) {
      const p=new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(matrix),q=uv.getElement(i,[]),x=p.x-ox,y=-p.z-oy;
      expect(Math.abs(q[0]-(c*x+s*y)/px)).toBeLessThan(.0001);
      expect(Math.abs(q[1]-(1-(-s*x+c*y)/py))).toBeLessThan(.0001);
    }
    for (let i=0;i<idx.getCount();i+=3) {
      const ps=[0,1,2].map(j=>new Vector3().fromArray(pos.getElement(idx.getScalar(i+j),[])).applyMatrix4(matrix));
      expect(contains(ps.reduce((v,p)=>v+p.x,0)/3,-ps.reduce((v,p)=>v+p.z,0)/3)).toBe(true);
      triangles++;
    }
  }
  expect(triangles).toBeGreaterThan(500);
});
