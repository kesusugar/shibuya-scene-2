import { describe, expect, it } from 'vitest';
import { readdirSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { NodeIO } from '@gltf-transform/core';
import { ASSET_LEVEL, LEVEL_BUDGET, SCENE_BUDGET } from '../src/perf/budget';

// Machine-independent performance budget (src/perf/budget.ts): triangles, draw primitives and bytes per asset.
const io = new NodeIO();
async function measure(dir: string) {
  let triangles = 0, primitives = 0, bytes = 0;
  for (const f of readdirSync(dir).filter((f) => f.endsWith('.glb'))) {
    const p = join(dir, f); bytes += statSync(p).size;
    const root = (await io.read(p)).getRoot();
    for (const node of root.listNodes()) {
      const mesh = node.getMesh(); if (!mesh) continue;
      for (const prim of mesh.listPrimitives()) {
        primitives++;
        const idx = prim.getIndices(); triangles += (idx ? idx.getCount() : prim.getAttribute('POSITION')!.getCount()) / 3;
      }
    }
  }
  return { triangles: Math.round(triangles), primitives, bytes };
}
const dirs: Record<string, string> = {};
for (const id of readdirSync('assets/buildings')) if (existsSync(join('assets/buildings', id, 'web'))) dirs[id] = join('assets/buildings', id, 'web');
for (const id of readdirSync('assets/ground')) if (existsSync(join('assets/ground', id, 'web'))) dirs[`ground/${id}`] = join('assets/ground', id, 'web');

describe('performance budget', async () => {
  const m: Record<string, Awaited<ReturnType<typeof measure>>> = {};
  for (const [id, dir] of Object.entries(dirs)) m[id] = await measure(dir);

  it('every shipped asset has a fidelity level', () => {
    for (const id of Object.keys(m)) expect(ASSET_LEVEL[id], `${id} has no level in src/perf/budget.ts`).toBeDefined();
  });
  it('each asset stays inside its level budget', () => {
    for (const [id, v] of Object.entries(m)) {
      const b = LEVEL_BUDGET[ASSET_LEVEL[id]];
      expect(v.triangles, `${id} triangles`).toBeLessThanOrEqual(b.triangles);
      expect(v.primitives, `${id} primitives`).toBeLessThanOrEqual(b.primitives);
      expect(v.bytes, `${id} bytes`).toBeLessThanOrEqual(b.bytes);
    }
  });
  it('the whole Core so far is inside the scene budget', () => {
    const t = Object.values(m).reduce((s, v) => ({ triangles: s.triangles + v.triangles, primitives: s.primitives + v.primitives, bytes: s.bytes + v.bytes }), { triangles: 0, primitives: 0, bytes: 0 });
    expect(t.triangles).toBeLessThanOrEqual(SCENE_BUDGET.triangles);
    expect(t.primitives).toBeLessThanOrEqual(SCENE_BUDGET.primitives);
    expect(t.bytes).toBeLessThanOrEqual(SCENE_BUDGET.bytes);
    console.log('core so far', JSON.stringify(t), JSON.stringify(m));
  });
});
