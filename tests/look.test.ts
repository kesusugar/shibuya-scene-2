import { describe, expect, it } from 'vitest';
import { Color, Group, Mesh, BoxGeometry, MeshStandardMaterial, MeshBasicMaterial, Texture } from 'three';
import { applyClassPass, applyLook, classify, LOOK_DEFAULT, parseLook } from '../src/world/look';

const mat = (name: string) => new MeshStandardMaterial({ name });
describe('material classes', () => {
  it('ground parts by mesh name', () => {
    expect(classify(mat('ground_asphalt'), 'ground_road')).toBe('road');
    expect(classify(mat('ground_sidewalk'), 'ground_sidewalk')).toBe('sidewalk');
    expect(classify(mat('ground_marking'), 'ground_marking')).toBe('marking');
    expect(classify(mat('ground_kerb'), 'ground_kerb')).toBe('kerb');
    expect(classify(mat('ground_fill_provisional'), 'ground_fill')).toBe('fill');
  });
  it('buildings by emissive-table kind first, then by name', () => {
    expect(classify(mat('tower_glass'), 'x', { tower_glass: { kind: 'glass', emit: [0, 0, 0], estr: 0 } })).toBe('glass');
    expect(classify(mat('starts_led'), 'x', { starts_led: { kind: 'led', emit: [1, 1, 1], estr: 2 } })).toBe('sign');
    expect(classify(mat('white_panel'), 'x')).toBe('wall');
    expect(classify(mat('shop_interior'), 'x')).toBe('interior');
    expect(classify(mat('steel_dark'), 'x', undefined, true)).toBe('sign');   // anything in an era sign layer
  });
});

describe('look parameters', () => {
  it('parses overrides and ignores unknown keys or bad numbers', () => {
    const l = parseLook('dayExposure:0.8,nope:3,road:abc');
    expect(l.dayExposure).toBe(0.8); expect(l.road).toBe(LOOK_DEFAULT.road); expect((l as unknown as Record<string, unknown>).nope).toBeUndefined();
  });
  it('sets ground albedo keeping the hue, and lights the ground only at night', () => {
    const g = new Group(); const m = new Mesh(new BoxGeometry(), new MeshStandardMaterial({ name: 'ground_sidewalk', color: new Color(0.3, 0.28, 0.25) }));
    m.name = 'ground_sidewalk'; g.add(m);
    const look = { ...LOOK_DEFAULT, sidewalk: 0.2, nightGround: 0.5 };
    applyLook(g, 'day', look); const s = m.material as MeshStandardMaterial;
    expect((s.color.r + s.color.g + s.color.b) / 3).toBeCloseTo(0.2, 5); expect(s.color.r).toBeGreaterThan(s.color.b);
    expect(s.emissive.r).toBe(0);
    applyLook(g, 'night', look); expect(s.emissive.r).toBeCloseTo(s.color.r * 0.5, 5);
  });
  it('gives glass and walls their own env map so the per-class intensity takes effect', () => {
    const g = new Group(); const glass = new Mesh(new BoxGeometry(), mat('tower_glass')); const wall = new Mesh(new BoxGeometry(), mat('white_panel')); g.add(glass, wall);
    const env = { map: new Texture(), intensity: 0.45 };
    applyLook(g, 'day', { ...LOOK_DEFAULT, glassEnv: 2, wallEnv: 0.5 }, undefined, env);
    expect((glass.material as MeshStandardMaterial).envMap).toBe(env.map);
    expect((glass.material as MeshStandardMaterial).envMapIntensity).toBeCloseTo(0.9, 6);
    expect((wall.material as MeshStandardMaterial).envMapIntensity).toBeCloseTo(0.225, 6);
  });
  it('class pass paints flat unlit colours', () => {
    const g = new Group(); const m = new Mesh(new BoxGeometry(), mat('tower_glass')); g.add(m);
    applyClassPass(g); expect((m.material as unknown as MeshBasicMaterial).isMeshBasicMaterial).toBe(true);
  });
});
