import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { BoxGeometry, Group, Matrix4, Mesh, MeshStandardMaterial, Vector3 } from 'three';
import { LAMP_CD, loadStreet, STREET_PARTS } from '../src/world/street';
import { LEVEL_BUDGET } from '../src/perf/budget';
import { classify } from '../src/world/look';

describe('Core street asset', async () => {
  const root = (await new NodeIO().read('assets/street/core/web/street_core.glb')).getRoot();
  const stats = JSON.parse(readFileSync('assets/street/core/source/data/street_stats.json', 'utf8'));
  const history = JSON.parse(readFileSync('assets/street/core/source/data/osm_2025.json', 'utf8'));

  it('exports finite geometry in the Core and common datum, without the imported ground', () => {
    const names = new Set<string>(); let tris = 0;
    for (const node of root.listNodes()) {
      const mesh = node.getMesh(); if (!mesh) continue;
      names.add(node.getName());
      const transform = new Matrix4().fromArray(node.getWorldMatrix());
      for (const prim of mesh.listPrimitives()) {
        expect(prim.getMaterial()).not.toBeNull();
        const a = prim.getAttribute('POSITION')!;
        tris += (prim.getIndices()?.getCount() ?? a.getCount()) / 3;
        for (let i = 0; i < a.getCount(); i++) {
          const p = new Vector3().fromArray(a.getElement(i, [])).applyMatrix4(transform);
          expect([p.x, p.y, p.z].every(Number.isFinite)).toBe(true);
          expect(Math.hypot(p.x - 6.5, p.z - 2)).toBeLessThan(55);
          expect(p.y).toBeGreaterThan(-6); expect(p.y).toBeLessThan(15);   // stair wells reach up to ~4.5 m below the pavement
        }
      }
    }
    expect([...names].sort()).toEqual([...STREET_PARTS].sort());
    expect(tris).toBeGreaterThan(1000); expect(tris).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);
  });

  it('has OSM-backed entrances and trees, and every rule-placed item records its rule', () => {
    expect(history.query_date).toBe('2025-10-31T23:59:59Z');
    const sourceIds = new Set(history.elements.map((e: { type: string; id: number }) => `${e.type}/${e.id}`));
    const mapped = stats.features.filter((f: { kind: string }) => f.kind === 'entrance' || f.kind === 'tree');
    expect(mapped.filter((f: { kind: string }) => f.kind === 'entrance')).toHaveLength(6);
    expect(mapped.filter((f: { kind: string }) => f.kind === 'tree')).toHaveLength(6);
    for (const f of mapped) {
      expect(sourceIds.has(f.id)).toBe(true);
      expect(f.shape_status).toMatch(/provisional/);
      expect(f.anchor_tp).toBeLessThanOrEqual(f.survey_max_tp);
    }
    for (const f of stats.features) { expect(f.anchor_tp).toBeGreaterThan(14); expect(f.anchor_tp).toBeLessThan(18); }
    const placed = stats.features.filter((f: { kind: string }) => f.kind !== 'entrance' && f.kind !== 'tree');
    expect(placed.length).toBeGreaterThanOrEqual(14);
    for (const f of placed) expect(f.placement).toMatch(/^rule R[12]$|^photo projection/);
    // the four OSM approach nodes each get exactly one vehicle mast (rule R2)
    const masts = placed.filter((f: { kind: string }) => f.kind === 'vehicle_signal').map((f: { osm_node: string }) => f.osm_node).sort();
    expect(masts).toEqual(stats.unresolved.filter((u: { kind: string }) => u.kind === 'signal').map((u: { id: string }) => u.id).sort());
    expect(stats.lights).toHaveLength(3);
    expect(stats.rail_length_m).toBeGreaterThan(100);
  });

  it('keeps railings on the pavement and out of every crosswalk', () => {
    const ground = JSON.parse(readFileSync('assets/ground/core/source/data/ground_input.json', 'utf8'));
    const layout = JSON.parse(readFileSync('assets/street/core/source/data/street_layout.json', 'utf8'));
    const inside = (p: number[], ring: number[][]) => {
      let c = false;
      for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
        const [xi, yi] = ring[i], [xj, yj] = ring[j];
        if ((yi > p[1]) !== (yj > p[1]) && p[0] < ((xj - xi) * (p[1] - yi)) / (yj - yi) + xi) c = !c;
      }
      return c;
    };
    for (const run of layout.rail_runs) for (const p of run) {
      for (const cw of ground.crosswalks) expect(inside(p, cw.band)).toBe(false);
      expect(Math.hypot(p[0] - 6.5, p[1] + 2)).toBeLessThan(52);
    }
  });

  it('keeps trees and furniture out of the photograph wall score', () => {
    expect(classify(new MeshStandardMaterial({ name: 'street_tree_leaves' }), 'x')).toBe('vegetation');
    expect(classify(new MeshStandardMaterial({ name: 'street_roof' }), 'x')).toBe('furniture');
  });
});

const fixture = () => {
  const root = new Group();
  for (const name of STREET_PARTS) {
    const m = new Mesh(new BoxGeometry(), new MeshStandardMaterial());
    m.name = name; root.add(m);
  }
  return root;
};
describe('street isolation and walking surfaces', () => {
  it('does not throw or add partial geometry when loading fails', async () => {
    const r = await loadStreet(async () => { throw new Error('missing GLB'); });
    expect(r.ok).toBe(false); expect(r.root.children).toHaveLength(0); expect(r.walkSurfaces).toHaveLength(0);
  });
  it('rejects an incomplete asset', async () => {
    const incomplete = fixture();
    incomplete.remove(incomplete.getObjectByName('street_roof')!);
    const r = await loadStreet(async () => incomplete);
    expect(r.ok).toBe(false); expect(r.error).toContain('missing street parts');
  });
  it('uses only entrance landings as walking surfaces, never canopy roofs or tree crowns', async () => {
    const r = await loadStreet(async () => fixture());
    expect(r.ok).toBe(true); expect(r.walkSurfaces.map((o) => o.name)).toEqual(['street_concrete']);
  });
  it('lights the lamps only at night', async () => {
    const f = fixture(); const anchor = new Group(); anchor.name = 'light_P01'; f.add(anchor);
    const r = await loadStreet(async () => f);
    expect(r.lights).toHaveLength(1); expect(r.lights[0].intensity).toBe(0);
    r.setTime('night'); expect(r.lights[0].intensity).toBe(LAMP_CD);
    r.setTime('day'); expect(r.lights[0].intensity).toBe(0);
  });
  it('removes trees from rendering and collisions for the one-change comparison', async () => {
    const r = await loadStreet(async () => fixture(), undefined, false);
    expect(r.ok).toBe(true); expect(r.root.getObjectByName('street_tree_leaves')).toBeUndefined();
    expect(r.root.getObjectByName('street_tree_bark')).toBeUndefined(); expect(r.stats.meshes).toBe(STREET_PARTS.length - 3);
  });
});
