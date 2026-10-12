import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Group, Mesh, BoxGeometry, MeshStandardMaterial } from 'three';
import { GROUND_PARTS, loadGround } from '../src/world/ground';
import { DATUM_TP, groundOffset } from '../src/world/buildings';

// The Core ground GLB (assets/ground/core): PLATEAU 2025 road surfaces in the common datum (Y = T.P. - 15.000 m).
const io = new NodeIO();
describe('Core ground asset', async () => {
  const root = (await io.read('assets/ground/core/web/ground_core.glb')).getRoot();
  const parts: Record<string, { tris: number; ymin: number; ymax: number; xz: [number, number, number, number] }> = {};
  for (const node of root.listNodes()) {
    const mesh = node.getMesh(); if (!mesh) continue;
    let tris = 0, ymin = Infinity, ymax = -Infinity; const xz: [number, number, number, number] = [Infinity, Infinity, -Infinity, -Infinity];
    const t = node.getTranslation();
    for (const prim of mesh.listPrimitives()) {
      expect(prim.getMaterial(), `${node.getName()} material`).not.toBeNull();
      const idx = prim.getIndices(); const a = prim.getAttribute('POSITION')!.getArray()!;
      tris += (idx ? idx.getCount() : a.length / 3) / 3;
      for (let i = 0; i < a.length; i += 3) {
        expect(Number.isFinite(a[i]) && Number.isFinite(a[i + 1]) && Number.isFinite(a[i + 2])).toBe(true);
        ymin = Math.min(ymin, a[i + 1] + t[1]); ymax = Math.max(ymax, a[i + 1] + t[1]);
        xz[0] = Math.min(xz[0], a[i] + t[0]); xz[1] = Math.min(xz[1], a[i + 2] + t[2]); xz[2] = Math.max(xz[2], a[i] + t[0]); xz[3] = Math.max(xz[3], a[i + 2] + t[2]);
      }
    }
    parts[node.getName()] = { tris, ymin, ymax, xz };
  }
  const stats = JSON.parse(readFileSync('assets/ground/core/source/data/ground_stats.json', 'utf8'));

  it('has every part, each with geometry', () => {
    for (const p of GROUND_PARTS) { expect(parts[p], p).toBeDefined(); expect(parts[p].tris, p).toBeGreaterThan(0); }
  });
  it('stays within a triangle budget for the whole Core ground', () => {
    const total = Object.values(parts).reduce((s, p) => s + p.tris, 0);
    // the glTF exporter drops zero-area triangles, so the shipped count is a little below Blender's polygon count
    expect(Math.abs(total - stats.triangles_total) / stats.triangles_total).toBeLessThan(0.05);
    expect(total).toBeLessThan(120_000);
  });
  it('heights are in the common datum: roads span the PLATEAU range T.P. 14.4..18.4', () => {
    for (const p of ['ground_road', 'ground_intersection']) {
      expect(parts[p].ymin).toBeGreaterThan(14.3 - DATUM_TP); expect(parts[p].ymax).toBeLessThan(18.5 - DATUM_TP);
    }
    // kerb faces and skirts reach at most 0.3 m below the surfaces they hang from
    expect(parts.ground_kerb.ymin).toBeGreaterThan(14.3 - DATUM_TP - 0.31);
  });
  it('covers the crossing: the road reaches past 50 m from the centre in every direction', () => {
    const [x0, z0, x1, z1] = parts.ground_road.xz;   // world X = east, Z = south; centre (6.5, -2.0) in plan = (6.5, 2.0) in world
    expect(x0).toBeLessThan(6.5 - 50); expect(x1).toBeGreaterThan(6.5 + 50); expect(z0).toBeLessThan(2.0 - 50); expect(z1).toBeGreaterThan(2.0 + 50);
  });
  it('sidewalks stand a kerb above the carriageway (PLATEAU has no kerb step of its own)', () => {
    expect(stats.params.kerb_height_m).toBeCloseTo(0.15, 5); expect(stats.params.kerb_low_m).toBeCloseTo(0.02, 5);
    expect(stats.kerb_length_m).toBeGreaterThan(500);
  });
  it('has the measured scramble crosswalks as zebra bars', () => {
    const input = JSON.parse(readFileSync('assets/ground/core/source/data/ground_input.json', 'utf8'));
    const ids = input.crosswalks.map((c: { id: string }) => c.id);
    expect(ids).toContain('way/754454449');        // the diagonal
    const diag = input.crosswalks.find((c: { id: string }) => c.id === 'way/754454449');
    expect(diag.width_source).toBe('orthophoto'); expect(diag.width_m).toBeGreaterThan(7); expect(diag.bars.length).toBeGreaterThan(8);
    expect(parts.ground_marking.ymin).toBeGreaterThan(parts.ground_road.ymin);
  });
});

describe('common datum and building offsets', () => {
  const v = (b: string) => JSON.parse(readFileSync(`assets/buildings/${b}/web/viewer.json`, 'utf8'));
  const anchors = JSON.parse(readFileSync('assets/ground/core/source/data/ground_anchors.json', 'utf8'));
  it('places each model 0 m on the lowest finished ground along its footprint (the base never floats)', () => {
    for (const b of ['qfront', 'magnet']) {
      expect(v(b).groundElevationTP).toBeCloseTo(anchors[b].anchor_tp, 6);
      expect(anchors[b].anchor_tp).toBeLessThanOrEqual(anchors[b].pavement_min_tp + 1e-9);
      expect(anchors[b].frontage_samples).toBeGreaterThan(50);
    }
    expect(groundOffset(v('qfront'))).toBeCloseTo(0.202, 3);
    expect(groundOffset(v('magnet'))).toBeCloseTo(-0.093, 3);
    expect(groundOffset(v('eiraku'))).toBeCloseTo(groundOffset(v('magnet')), 6);   // modelled in MAGNET's file
  });
  it('keeps the roofs within 0.5 m of PLATEAU after the move', () => {
    for (const b of ['qfront', 'magnet']) expect(Math.abs(anchors[b].roof_deviation_vs_plateau_m)).toBeLessThan(0.5);
  });
  it('an asset that does not state its elevation stays at 0 (backward compatible)', () => {
    expect(groundOffset({})).toBe(0);
  });
});

describe('loadGround isolation', () => {
  it('never throws: a failed load returns an empty root and the error', async () => {
    const r = await loadGround(async () => { throw new Error('404'); });
    expect(r.ok).toBe(false); expect(r.root.children.length).toBe(0); expect(r.error).toContain('404');
  });
  it('reports missing parts instead of failing', async () => {
    const g = new Group(); const m = new Mesh(new BoxGeometry(10, 1, 10), new MeshStandardMaterial()); m.name = 'ground_road'; g.add(m);
    const r = await loadGround(async () => g);
    expect(r.ok).toBe(true); expect(r.missing).toContain('ground_marking'); expect(r.missing).not.toContain('ground_road');
  });
});
