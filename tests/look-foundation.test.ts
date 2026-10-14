import { describe, expect, it } from 'vitest';
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Texture } from 'three';
import { addDetail, applySurfaceDetail, detailKind, makeDetailTexture } from '../src/world/surface-detail';
import { applyAtmosphere, SKY } from '../src/world/atmosphere';
import { loadProps } from '../src/world/props';
import { classify } from '../src/world/look';
import { Scene } from 'three';

describe('surface detail', () => {
  const tex = makeDetailTexture(64, 7);
  it('is deterministic and keeps the mean multiplier channels centred (C3a albedo kept on average)', () => {
    const again = makeDetailTexture(64, 7);
    expect(Array.from(again.image.data as Uint8Array)).toEqual(Array.from(tex.image.data as Uint8Array));
    const d = tex.image.data as Uint8Array; let r = 0, a = 0; const n = d.length / 4;
    for (let i = 0; i < d.length; i += 4) { r += d[i]; a += d[i + 3]; }
    expect(r / n / 255).toBeGreaterThan(0.35); expect(r / n / 255).toBeLessThan(0.65);
    expect(a / n / 255).toBeGreaterThan(0.35); expect(a / n / 255).toBeLessThan(0.65);
  });
  it('chooses the kind from the look class and never overrides an existing texture', () => {
    const m = (name: string) => new MeshStandardMaterial({ name });
    expect(detailKind(classify(m('ground_asphalt'), 'ground_road'), m('ground_asphalt'))).toBe('road');
    expect(detailKind(classify(m('ground_sidewalk'), 'ground_sidewalk'), m('ground_sidewalk'))).toBe('paving');
    expect(detailKind(classify(m('ground_kerb'), 'ground_kerb'), m('ground_kerb'))).toBe('plain');
    expect(detailKind(classify(m('ctx_wall_ribbon_a'), 'x'), m('ctx_wall_ribbon_a'))).toBe('wall');
    const textured = m('ground_sidewalk_pavers'); textured.map = new Texture();
    expect(detailKind('sidewalk', textured)).toBeNull();
    expect(detailKind(classify(m('tower_glass'), 'x'), m('tower_glass'))).toBeNull();
  });
  it('injects world-space shading once per material and limits kinds when asked', () => {
    const g = new Group();
    const wall = new Mesh(new BoxGeometry(), new MeshStandardMaterial({ name: 'ctx_wall_punched_a' }));
    const road = new Mesh(new BoxGeometry(), new MeshStandardMaterial({ name: 'ground_asphalt' })); road.name = 'ground_road';
    g.add(wall, road);
    expect(applySurfaceDetail(g, tex, ['wall'])).toBe(1);
    expect((road.material as MeshStandardMaterial).userData.surfaceDetail).toBeUndefined();
    expect(applySurfaceDetail(g, tex)).toBe(2);
    const mat = wall.material as MeshStandardMaterial; const before = mat.onBeforeCompile;
    addDetail(mat, 'wall', tex); expect(mat.onBeforeCompile).toBe(before);
    const shader = { uniforms: {} as Record<string, unknown>, vertexShader: '#include <common>\n#include <project_vertex>', fragmentShader: '#include <common>\n#include <map_fragment>\n#include <roughnessmap_fragment>' };
    (mat.onBeforeCompile as unknown as (s: typeof shader) => void)(shader);
    expect(shader.vertexShader).toContain('vDetailWorld'); expect(shader.fragmentShader).toContain('diffuseColor.rgb *= k');
    expect(mat.customProgramCacheKey()).toBe('surface-detail-wall');
  });
});

describe('atmosphere', () => {
  it('adds distance fog in the horizon colour and removes it for ?sky=flat', () => {
    const s = new Scene(); applyAtmosphere(s, 'day');
    expect(s.fog).not.toBeNull(); expect(s.fog!.color.getHex()).toBe(SKY.day.horizon);
    applyAtmosphere(s, 'day', false); expect(s.fog).toBeNull();
  });
});

describe('imported props', () => {
  const part = () => { const g = new Group(); const m = new Mesh(new BoxGeometry(), new MeshStandardMaterial({ name: 'prop_furniture_0' })); m.name = 'body'; g.add(m); return g; };
  const layout = { props: { bin: { file: 'bin.glb' } }, placements: [
    { prop: 'bin', xy: [1, 2] as [number, number], basis: 'test' }, { prop: 'bin', xy: [5, 5] as [number, number], basis: 'test' }, { prop: 'bin', xy: [99, 99] as [number, number], basis: 'off the walking surface' }] };
  it('instances each part once, snaps to the ground and skips placements without ground', async () => {
    const r = await loadProps(async () => part(), async <T>() => layout as unknown as T, (x) => (x > 50 ? null : 0.3));
    expect(r.ok).toBe(true); expect(r.stats).toEqual({ placed: 2, skipped: 1, draws: 1 });
    const inst = r.root.children[0].children[0] as unknown as { count: number; getMatrixAt(i: number, m: import('three').Matrix4): void };
    expect(inst.count).toBe(2);
  });
  it('fails without throwing and leaves nothing behind', async () => {
    const r = await loadProps(async () => { throw new Error('x'); }, async <T>() => layout as unknown as T, () => 0);
    expect(r.ok).toBe(false); expect(r.root.children).toHaveLength(0);
  });
});
