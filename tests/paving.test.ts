import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3 } from 'three';

const config = JSON.parse(readFileSync('assets/ground/core/source/data/paving_layout.json', 'utf8'));

it('textures only the two dedicated paving materials and retains a portable ground tint', async () => {
  const root = (await new NodeIO().read('assets/ground/core/web/ground_core.glb')).getRoot();
  const paving = root.listMaterials().find(m => m.getName() === 'ground_sidewalk_pavers')!;
  expect(paving.getBaseColorTexture()).not.toBeNull();
  expect(paving.getBaseColorFactor()).toEqual([.30, .28, .25, 1]);
  expect(paving.getBaseColorTextureInfo()!.getWrapS()).toBe(10497);
  expect(paving.getBaseColorTextureInfo()!.getWrapT()).toBe(10497);
  for (const m of root.listMaterials().filter(m => !['ground_sidewalk_pavers', 'ground_sidewalk_plaza_pavers'].includes(m.getName()))) expect(m.getBaseColorTexture()).toBeNull();
});

it('keeps the paving within the north-area mask and uses plan metres for the block scale', async () => {
  const root = (await new NodeIO().read('assets/ground/core/web/ground_core.glb')).getRoot();
  const angle = config.yaw_deg*Math.PI/180, c = Math.cos(angle), s = Math.sin(angle);
  const [px,py] = config.tile_size_m.map((n: number,i: number) => n*config.atlas_tiles[i]);
  const [x0,y0,x1,y1] = config.bounds_xy_m;
  let triangles = 0;
  for (const node of root.listNodes()) for (const prim of node.getMesh()?.listPrimitives() ?? []) {
    if (prim.getMaterial()!.getName() !== 'ground_sidewalk_pavers') continue;
    const matrix = new Matrix4().fromArray(node.getWorldMatrix()), pos = prim.getAttribute('POSITION')!, uv = prim.getAttribute('TEXCOORD_0')!, idx = prim.getIndices()!;
    for (let i=0; i<pos.getCount(); i+=Math.max(1,Math.floor(pos.getCount()/500))) {
      const p = new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(matrix), q = uv.getElement(i,[]), y = -p.z;
      expect(Math.abs(q[0]-(c*p.x+s*y)/px)).toBeLessThan(.0001);
      expect(Math.abs(q[1]-(1-(-s*p.x+c*y)/py))).toBeLessThan(.0001);
    }
    for (let i=0; i<idx.getCount(); i+=3) {
      const points = [0,1,2].map(j => new Vector3().fromArray(pos.getElement(idx.getScalar(i+j),[])).applyMatrix4(matrix));
      const x = points.reduce((a,p) => a+p.x,0)/3, y = -points.reduce((a,p) => a+p.z,0)/3;
      expect(x).toBeGreaterThanOrEqual(x0-.001); expect(x).toBeLessThanOrEqual(x1+.001);
      expect(y).toBeGreaterThanOrEqual(y0-.001); expect(y).toBeLessThanOrEqual(y1+.001); triangles++;
    }
  }
  expect(triangles).toBeGreaterThan(1000);
});
