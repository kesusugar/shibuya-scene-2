import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Texture } from 'three';
import { CONTEXT_TINTS, loadContext } from '../src/world/context';

describe('C-level context asset', async () => {
  const root = (await new NodeIO().read('assets/context/core/web/context_core.glb')).getRoot();
  const stats = JSON.parse(readFileSync('assets/context/core/source/data/context_stats.json', 'utf8'));

  it('never duplicates a building that has its own asset or the street entrances', () => {
    const ids = new Set(stats.buildings.map((b: { id: string }) => b.id));
    for (const own of ['way/136691386', 'way/116806281']) expect(ids.has(own)).toBe(false);   // QFRONT, MAGNET (+ Eiraku)
    expect(stats.excluded.map((e: { id: string }) => e.id).sort()).toEqual(expect.arrayContaining(['way/116806281', 'way/136691386']));
    const plateau = stats.buildings.map((b: { plateau_id: string }) => b.plateau_id);
    expect(new Set(plateau).size).toBe(plateau.length);
  });

  it('keeps every shell in the common datum and names its parts by group and material', () => {
    const names = root.listNodes().filter((n) => n.getMesh()).map((n) => n.getName());
    expect(names).toContain('core__ctx_roof');
    for (const n of names) expect(n).toMatch(/^(core|station)__ctx_(roof|structure|wall_(ribbon|punched)_[ab])$/);
    for (const n of names) if (n.includes('_wall_')) expect(CONTEXT_TINTS[n.split('__')[1]]).toBeDefined();
    for (const b of stats.buildings) expect(b.faces).toBeGreaterThan(0);
  });
});

const fixture = () => {
  const g = new Group();
  for (const name of ['core__ctx_roof', 'core__ctx_wall_ribbon_a', 'station__ctx_wall_punched_b']) {
    const m = new Mesh(new BoxGeometry(10, 10, 10), new MeshStandardMaterial({ name: name.split('__')[1] })); m.name = name; g.add(m);
  }
  return g;
};
describe('context loading', () => {
  const tex = async () => new Texture();
  it('does not throw or add geometry when loading fails', async () => {
    const r = await loadContext(async () => { throw new Error('missing'); }, undefined, true, tex);
    expect(r.ok).toBe(false); expect(r.root.children).toHaveLength(0);
  });
  it('tints walls, hides the station group on request and lights windows only at night', async () => {
    const r = await loadContext(async () => fixture(), undefined, false, tex);
    expect(r.ok).toBe(true);
    const wall = r.root.getObjectByName('core__ctx_wall_ribbon_a') as Mesh;
    const m = wall.material as MeshStandardMaterial;
    expect(m.color.getHex()).toBe(CONTEXT_TINTS.ctx_wall_ribbon_a);
    expect(r.root.getObjectByName('station__ctx_wall_punched_b')!.visible).toBe(false);
    expect(m.emissiveIntensity).toBe(0);
    r.setTime('night'); expect(m.emissiveIntensity).toBeGreaterThan(0); expect(m.emissiveMap).not.toBeNull();
    r.setTime('day'); expect(m.emissiveIntensity).toBe(0);
  });
});
