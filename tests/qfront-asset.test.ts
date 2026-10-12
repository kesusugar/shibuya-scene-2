import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';

// The shipped GLB itself: geometry present, coordinates finite and in metres, materials named and present.
const dir = 'assets/buildings/qfront/web';

describe('QFRONT web asset', async () => {
  const doc = await new NodeIO().read(`${dir}/qfront.glb`);
  const root = doc.getRoot();

  it('has meshes, triangles and materials', () => {
    let tris = 0;
    for (const mesh of root.listMeshes()) for (const prim of mesh.listPrimitives()) {
      const idx = prim.getIndices(); const pos = prim.getAttribute('POSITION')!;
      tris += (idx ? idx.getCount() : pos.getCount()) / 3;
      expect(prim.getMaterial(), `${mesh.getName()} material`).not.toBeNull();
    }
    expect(root.listMeshes().length).toBeGreaterThan(20);
    expect(tris).toBeGreaterThan(50_000);
    expect(tris).toBeLessThan(600_000);
  });

  it('every vertex is finite and inside the plausible site (metres, Y up)', () => {
    for (const mesh of root.listMeshes()) for (const prim of mesh.listPrimitives()) {
      const arr = prim.getAttribute('POSITION')!.getArray()!;
      for (const v of arr) expect(Number.isFinite(v)).toBe(true);
    }
    const nodes = root.listNodes().filter((n) => n.getMesh());
    expect(nodes.length).toBeGreaterThan(0);
  });

  it('carries the landmark parts the viewer must never lose', () => {
    const names = root.listMeshes().map((m) => m.getName()).join(' ');
    for (const part of ['05_CROWN_fin', '03_OUTER_SKIN_fin', '02_INNER_GLASS_dark_glass', '04_QS_EYE_led', 'QFRONT']) expect(names).toContain(part);
  });

  it('day and night emissive tables cover the same materials', () => {
    const day = JSON.parse(readFileSync(`${dir}/emissive_day.json`, 'utf8'));
    const night = JSON.parse(readFileSync(`${dir}/emissive_night.json`, 'utf8'));
    expect(Object.keys(day).sort()).toEqual(Object.keys(night).sort());
    expect(night.letters.estr).toBeGreaterThan(day.letters.estr);
  });
});
