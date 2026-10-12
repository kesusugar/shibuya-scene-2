import { expect, it } from 'vitest';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BoxGeometry, Group, Mesh, MeshStandardMaterial } from 'three';
import { loadProjectedStreet, type ProjectedMetadata } from '../src/world/projected-street';
const metadata = (): ProjectedMetadata => ({
  status: 'experimental_only', camera_status: 'provisional',
  camera: { photo: 'test', pos: [0, 0, 10], yaw: 0, pitch: -45, roll: 0, fpx: 100, W: 100, H: 100 },
  light_points: [0, 1, 2].map((i) => ({ id: `P${i}`, position: [i, 7, 0], intensity_cd: 1800, status: 'provisional' })),
});
const asset = () => {
  const g = new Group();
  for (const name of ['street_provisional_pole', 'street_lamp_glass', 'street_signal_body', 'street_signal_green', 'street_sign_blue', 'street_sign_red']) {
    const m = new Mesh(new BoxGeometry(), new MeshStandardMaterial({ name })); m.name = name; g.add(m);
  }
  return g;
};
const io = (data = metadata()) => ({ loadGlb: async () => asset(), loadJson: async <T>() => data as T });
it('uses real spot lights only at night and allows an isolated lights-off comparison', async () => {
  const result = await loadProjectedStreet(io());
  expect(result.ok).toBe(true); expect(result.metadata?.status).toBe('experimental_only');
  expect(result.lights.map((l) => l.intensity)).toEqual([0, 0, 0]);
  result.setTime('night'); expect(result.lights.map((l) => l.intensity)).toEqual([1800, 1800, 1800]);
  result.setTime('night', false); expect(result.lights.map((l) => l.intensity)).toEqual([0, 0, 0]);
  result.setTime('day'); expect(result.lights.every((l) => !l.castShadow && l.intensity === 0)).toBe(true);
});
it('rejects unmarked or non-finite lamp placements without exporting partial lights', async () => {
  const data = metadata(); data.light_points[1].position[0] = NaN;
  const r = await loadProjectedStreet(io(data)); expect(r.ok).toBe(false); expect(r.root.children).toHaveLength(0); expect(r.lights).toHaveLength(0);
});
it('isolates missing experimental assets from the normal scene', async () => {
  const r = await loadProjectedStreet({ ...io(), loadGlb: async () => { throw new Error('missing experiment'); } });
  expect(r.ok).toBe(false); expect(r.error).toContain('missing experiment'); expect(r.root.children).toHaveLength(0);
});

it('keeps the actual experimental GLB finite and in the ground datum, with all six expected parts', async () => {
  const root = (await new NodeIO().read('assets/street/core/web/street_projected.glb')).getRoot();
  const names = [];
  for (const node of root.listNodes()) {
    if (!node.getMesh()) continue;
    names.push(node.getName());
    const matrix = new Matrix4().fromArray(node.getWorldMatrix());
    for (const primitive of node.getMesh()!.listPrimitives()) {
      const position = primitive.getAttribute('POSITION')!;
      for (let i = 0; i < position.getCount(); i++) {
        const p = new Vector3().fromArray(position.getElement(i, [])).applyMatrix4(matrix);
        expect([p.x, p.y, p.z].every(Number.isFinite)).toBe(true);
        expect(Math.abs(p.x)).toBeLessThan(55); expect(Math.abs(p.z)).toBeLessThan(55);
        expect(p.y).toBeGreaterThan(-1); expect(p.y).toBeLessThan(15);
      }
    }
  }
  expect(names.sort()).toEqual(['street_provisional_pole', 'street_lamp_glass', 'street_signal_body', 'street_signal_green', 'street_sign_blue', 'street_sign_red'].sort());
});
