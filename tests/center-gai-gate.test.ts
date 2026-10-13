import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';

const base = 'assets/buildings/center-gai-gate/';
const json = (path: string) => JSON.parse(readFileSync(path, 'utf8'));
async function meshes(path: string, offset = 0) {
  const root = (await new NodeIO().read(path)).getRoot(), result: Mesh[] = [];
  for (const node of root.listNodes()) for (const primitive of node.getMesh()?.listPrimitives() ?? []) {
    const matrix = new Matrix4().fromArray(node.getWorldMatrix()), pos = primitive.getAttribute('POSITION')!;
    const points: number[] = [];
    for (let i = 0; i < pos.getCount(); i++) {
      const p = new Vector3().fromArray(pos.getElement(i, [])).applyMatrix4(matrix); p.y += offset;
      points.push(p.x, p.y, p.z);
    }
    const geo = new BufferGeometry(); geo.setAttribute('position', new Float32BufferAttribute(points, 3));
    const idx = primitive.getIndices(); if (idx) geo.setIndex(Array.from(idx.getArray()!));
    const mesh = new Mesh(geo, new MeshBasicMaterial({ side: DoubleSide })); mesh.name = primitive.getMaterial()!.getName(); result.push(mesh);
  }
  return result;
}
function dispose(objects: Mesh[]) { for (const o of objects) { o.geometry.dispose(); (o.material as MeshBasicMaterial).dispose(); } }

it('anchors both bases to measured C2a pavement in the common T.P.15 datum', async () => {
  const stats = json(base+'source/data/stats.json'), objects = await meshes(base+'web/center-gai-gate.glb');
  try {
    expect(json(base+'web/viewer.json').groundElevationTP).toBe(15);
    expect(stats.feet).toHaveLength(2);
    const bases = objects.filter(o => o.name === 'gate_base');
    for (const foot of stats.feet) {
      expect(foot.samples.length).toBe(5);
      const points: Vector3[] = [];
      for (const b of bases) {
        const pos = b.geometry.getAttribute('position');
        for (let i = 0; i < pos.count; i++) {
          const p = new Vector3().fromBufferAttribute(pos, i);
          if (Math.hypot(p.x-foot.xy[0], p.z+foot.xy[1]) < .4) points.push(p);
        }
      }
      expect(Math.min(...points.map(p => p.y))).toBeCloseTo(foot.min_tp-15-.025, 3);
    }
  } finally { dispose(objects); }
});

it('keeps the passage open at walking height while the posts remain collidable', async () => {
  const objects = await meshes(base+'web/center-gai-gate.glb');
  try {
    const layout = json(base+'source/data/layout.json'), stats = json(base+'source/data/stats.json');
    const a = new Vector3(layout.foot_points[0][0], 1.9, -layout.foot_points[0][1]);
    const b = new Vector3(layout.foot_points[1][0], 1.9, -layout.foot_points[1][1]);
    const tangent = b.clone().sub(a).normalize(), forward = new Vector3(-tangent.z, 0, tangent.x);
    const centre = a.clone().add(b).multiplyScalar(.5);
    const ray = new Raycaster(centre.clone().addScaledVector(forward, 3), forward.clone().negate(), 0, 6);
    expect(ray.intersectObjects(objects, false)).toHaveLength(0);
    ray.set(a.clone().addScaledVector(forward, 1), forward.clone().negate()); ray.far = 2;
    expect(ray.intersectObjects(objects, false)[0]?.object.name).toBe('gate_frame');
    expect(stats.min_clear_height_m).toBeGreaterThan(4);
  } finally { dispose(objects); }
});

it('keeps the estimated footings clear of existing QFRONT and west-block wall surfaces', async () => {
  const objects: Mesh[] = [];
  try {
    for (const id of ['qfront', 'west-block']) {
      const offset = json(`assets/buildings/${id}/web/viewer.json`).groundElevationTP-15;
      objects.push(...await meshes(`assets/buildings/${id}/web/${id}.glb`, offset));
    }
    for (const foot of json(base+'source/data/stats.json').feet) {
      const origin = new Vector3(foot.xy[0], foot.tp-15+1, -foot.xy[1]);
      for (const direction of [new Vector3(1,0,0),new Vector3(-1,0,0),new Vector3(0,0,1),new Vector3(0,0,-1)]) {
        expect(new Raycaster(origin, direction, 0, .4).intersectObjects(objects, false)).toHaveLength(0);
      }
    }
  } finally { dispose(objects); }
});
