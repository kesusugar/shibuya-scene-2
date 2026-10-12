import { describe, expect, it } from 'vitest';
import { BoxGeometry, BufferAttribute, BufferGeometry, Group, Mesh, MeshStandardMaterial } from 'three';
import { applyEmissive, loadBuilding, validateBuilding, type BuildingIO } from '../src/world/buildings';

const hints = { arcMid: [0, 0], arcNormal: [0, -1], arcEnds: [[1, 0], [-1, 0]], floodlights: { arcStart_m: [30, 35], arcEnd_m: [30, 35] },
  planBounds: [0, 0, 1, 1], crownTop_m: 52, cameraQ032: { D: 60, lat: 0, yaw: 0, fpx: 1600, cx: 640, cy: 1500, W: 1280, H: 1749, height_m: 1.6 }, sun: { azimuth_deg: 152, elevation_deg: 38 } };

function okBuilding() {
  const g = new Group();
  const m = new Mesh(new BoxGeometry(20, 50, 20), new MeshStandardMaterial({ name: 'letters' }));
  g.add(m);
  return g;
}
const io = (root: () => Promise<Group>): BuildingIO => ({
  loadGlb: () => root(),
  loadJson: async (url) => (url.endsWith('viewer.json') ? hints : { letters: { kind: 'opaque', emit: [1, 1, 1], estr: url.includes('night') ? 4 : 0 } }) as never,
});

describe('loadBuilding isolation', () => {
  it('returns the model and stats when the asset is sound', async () => {
    const r = await loadBuilding('a', io(async () => okBuilding()));
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.stats.triangles).toBe(12);
  });
  it('never throws: a network failure gives a placeholder and an error', async () => {
    const r = await loadBuilding('b', io(async () => { throw new Error('404'); }));
    expect(r.ok).toBe(false);
    expect(r.root.children.length).toBe(1);
    if (!r.ok) expect(r.error).toContain('404');
  });
  it('rejects an empty or corrupt asset instead of showing nothing', async () => {
    const empty = await loadBuilding('c', io(async () => new Group()));
    expect(empty.ok).toBe(false);
    const nanGeo = new BufferGeometry(); nanGeo.setAttribute('position', new BufferAttribute(new Float32Array([0, 0, 0, NaN, 1, 0, 1, 1, 0]), 3));
    const g = new Group(); g.add(new Mesh(nanGeo, new MeshStandardMaterial()));
    expect(validateBuilding(g).some((p) => p.includes('non-finite'))).toBe(true);
  });
  it('one failing building does not affect another', async () => {
    const [bad, good] = await Promise.all([loadBuilding('bad', io(async () => { throw new Error('x'); })), loadBuilding('good', io(async () => okBuilding()))]);
    expect(bad.ok).toBe(false); expect(good.ok).toBe(true);
  });
  it('switches emissive strength between the day and night tables', async () => {
    const r = await loadBuilding('d', io(async () => okBuilding()));
    if (!r.ok) throw new Error(r.error);
    const mat = (r.root.children[0].children[0] as Mesh).material as MeshStandardMaterial;
    applyEmissive(r.root, r.emissive.night); expect(mat.emissiveIntensity).toBe(4);
    applyEmissive(r.root, r.emissive.day); expect(mat.emissiveIntensity).toBe(0);
  });
});
