import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';

// The shipped MAGNET GLBs: building, 2025 sign layer and the separate Eiraku building.
const io = new NodeIO();
const tris = async (path: string) => {
  const root = (await io.read(path)).getRoot();
  let n = 0;
  for (const mesh of root.listMeshes()) for (const prim of mesh.listPrimitives()) {
    const idx = prim.getIndices(); const pos = prim.getAttribute('POSITION')!;
    n += (idx ? idx.getCount() : pos.getCount()) / 3;
    expect(prim.getMaterial(), `${mesh.getName()} material`).not.toBeNull();
    for (const v of pos.getArray()!) expect(Number.isFinite(v)).toBe(true);
  }
  return { root, n };
};
const bounds = (root: Awaited<ReturnType<typeof tris>>['root']) => {
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (const node of root.listNodes()) {
    const mesh = node.getMesh(); if (!mesh) continue;
    const t = node.getTranslation();
    for (const prim of mesh.listPrimitives()) {
      const a = prim.getAttribute('POSITION')!.getArray()!;
      for (let i = 0; i < a.length; i += 3) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], a[i + k] + t[k]); hi[k] = Math.max(hi[k], a[i + k] + t[k]); }
    }
  }
  return { lo, hi };
};

describe('MAGNET web assets', async () => {
  const magnet = await tris('assets/buildings/magnet/web/magnet.glb');
  const signs = await tris('assets/buildings/magnet/web/magnet_signs_2025.glb');
  const eiraku = await tris('assets/buildings/eiraku/web/eiraku.glb');

  it('each GLB has geometry within a plausible budget', () => {
    expect(magnet.n).toBeGreaterThan(5_000); expect(magnet.n).toBeLessThan(300_000);
    expect(signs.n).toBeGreaterThan(500); expect(eiraku.n).toBeGreaterThan(100);
  });

  it('sits on the PLATEAU footprint in world axes (X east, Y up, Z south) and keeps the height kinds apart', () => {
    const { lo, hi } = bounds(magnet.root);
    // plan x 25.7..51.7 east, north 9.9..71.2 -> z -71.2..-9.9 (a little slack for canopies and the truss)
    expect(lo[0]).toBeGreaterThan(22); expect(hi[0]).toBeLessThan(55);
    expect(lo[2]).toBeGreaterThan(-75); expect(hi[2]).toBeLessThan(-7);
    expect(lo[1]).toBeGreaterThan(-0.5);
    // tower parapet 42.42 m + roof antennas (7 m): never the 34.2 m buildingHeight alone
    expect(hi[1]).toBeGreaterThan(42); expect(hi[1]).toBeLessThan(52);
  });

  it('keeps the era layer separate: no sign materials in the building GLB, none of the building in the layer', () => {
    const mNames = magnet.root.listMaterials().map((m) => m.getName());
    const sNames = signs.root.listMaterials().map((m) => m.getName());
    for (const s of ['magnet_logo', 'box_screen', 'drum_wrap', 'eiraku_acom']) { expect(sNames).toContain(s); expect(mNames).not.toContain(s); }
    expect(mNames).toContain('tower_glass'); expect(sNames).not.toContain('tower_glass');
  });

  it('viewer hints declare the layer and a photo-fitted camera', () => {
    const v = JSON.parse(readFileSync('assets/buildings/magnet/web/viewer.json', 'utf8'));
    expect(v.layers.signs_2025).toBe('magnet_signs_2025.glb');
    expect(v.cameraFit.photo).toContain('M027');
    expect(v.cameraFit.fpx).toBeGreaterThan(500);
  });

  it('day and night emissive tables cover the same materials; screens are brighter at night', () => {
    for (const id of ['magnet', 'eiraku']) {
      const day = JSON.parse(readFileSync(`assets/buildings/${id}/web/emissive_day.json`, 'utf8'));
      const night = JSON.parse(readFileSync(`assets/buildings/${id}/web/emissive_night.json`, 'utf8'));
      expect(Object.keys(day).sort()).toEqual(Object.keys(night).sort());
      expect(night.box_screen.estr).toBeGreaterThan(day.box_screen.estr);
    }
  });
});
