import { expect, it } from 'vitest';
import { readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { NodeIO } from '@gltf-transform/core';
import { Group, Mesh, MeshStandardMaterial, Matrix4, BufferAttribute, BufferGeometry, DoubleSide, MeshBasicMaterial, Raycaster, Vector3 } from 'three';
import { loadHachiko, HACHIKO_SCAN_PLACEMENT } from '../src/world/hachiko';

it('loads exactly one complete scan with one rigid placement and isolates failure', async () => {
  const scene = new Group(), geo = new BufferGeometry();
  const actual = (await new NodeIO().read('assets/street/hachiko/web/hachiko.glb')).getRoot().listMeshes()[0].listPrimitives()[0];
  geo.setAttribute('position', new BufferAttribute(actual.getAttribute('POSITION')!.getArray()!, 3));
  geo.setIndex(new BufferAttribute(actual.getIndices()!.getArray()!, 1));
  const mesh = new Mesh(geo, new MeshStandardMaterial()); mesh.name = 'hachiko_uploaded_scan_candidate_v001'; scene.add(mesh);
  const loaded = await loadHachiko(async () => scene);
  expect(loaded.ok).toBe(true); expect(loaded.stats).toEqual({ meshes: 1, triangles: 85_934 });
  expect(loaded.root.position.toArray()).toEqual([...HACHIKO_SCAN_PLACEMENT.position]);
  expect(loaded.root.scale.toArray()).toEqual([1, 1, 1]); expect(mesh.castShadow).toBe(true);
  expect(loaded.root.children).toEqual([scene]);
  const failed = await loadHachiko(async () => { throw Error('unavailable'); });
  expect(failed.ok).toBe(false); expect(failed.root.children).toHaveLength(0);
  expect((await loadHachiko(async () => new Group())).ok).toBe(false);
});

it('preserves the canonical geometry, UVs, normals and material values in the budgeted runtime derivative', async () => {
  const io = new NodeIO();
  const canonical = (await io.read('assets/street/hachiko/source/scan-candidate/model/hachiko_uploaded_scan_candidate_v001.glb')).getRoot();
  const web = (await io.read('assets/street/hachiko/web/hachiko.glb')).getRoot();
  expect(web.listMeshes()).toHaveLength(1);
  const a = canonical.listMeshes()[0].listPrimitives()[0], b = web.listMeshes()[0].listPrimitives()[0];
  for (const semantic of a.listSemantics()) {
    const source = a.getAttribute(semantic)!.getArray()!, runtime = b.getAttribute(semantic)!.getArray()!;
    expect(Buffer.from(runtime.buffer, runtime.byteOffset, runtime.byteLength)).toEqual(Buffer.from(source.buffer, source.byteOffset, source.byteLength));
  }
  expect(b.getIndices()!.getArray()).toEqual(a.getIndices()!.getArray());
  expect(b.getIndices()!.getCount() / 3).toBe(85_934);
  expect(web.listMaterials()[0].getMetallicFactor()).toBe(.25);
  expect(web.listMaterials()[0].getRoughnessFactor()).toBe(.2);
  expect(statSync('assets/street/hachiko/web/hachiko.glb').size).toBeLessThanOrEqual(3_000_000);
  expect(web.listNodes().map(n => n.getName())).not.toContain('street_hachiko_dog');
  expect(web.listNodes()[0].getMatrix()).toEqual(new Matrix4().toArray());
});

it('keeps the canonical delivery and old complete asset recoverable outside the served web folder', () => {
  const sha = (p: string) => createHash('sha256').update(readFileSync(p)).digest('hex');
  expect(sha('assets/street/hachiko/source/scan-candidate/model/hachiko_uploaded_scan_candidate_v001.glb')).toBe('cd20601d57308a1b50892c05d509a6295ca24ca2045cfd37421995a840bf039e');
  expect(sha('assets/street/hachiko/source/legacy/hachiko.glb')).toBe('370db19f30af6c4c3ab9d49ae910fa99e14643fc507630f90655cf6d220d0ae5');
});

it('fits all 371 retained rim points on the actual sidewalk without an open floating edge', async () => {
  const placement = JSON.parse(readFileSync('assets/street/hachiko/source/data/scan-placement.json', 'utf8'));
  expect(placement.position).toEqual([...HACHIKO_SCAN_PLACEMENT.position]);
  const matrix = new Matrix4().makeTranslation(...HACHIKO_SCAN_PLACEMENT.position).multiply(new Matrix4().makeRotationY(HACHIKO_SCAN_PLACEMENT.yawDegrees * Math.PI / 180));
  expect(matrix.toArray()).toEqual(placement.matrixColumnMajor);
  const surfaces: Mesh[] = [];
  for (const n of (await new NodeIO().read('assets/ground/core/web/ground_core.glb')).getRoot().listNodes()) {
    if (!n.getName().startsWith('ground_sidewalk')) continue;
    for (const p of n.getMesh()?.listPrimitives() ?? []) {
      const geo = new BufferGeometry().setAttribute('position', new BufferAttribute(p.getAttribute('POSITION')!.getArray()!, 3));
      geo.setIndex(new BufferAttribute(p.getIndices()!.getArray()!, 1)); geo.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
      const mesh = new Mesh(geo, new MeshBasicMaterial({ side: DoubleSide })); mesh.updateMatrixWorld(); surfaces.push(mesh);
    }
  }
  const ray = new Raycaster(); expect(placement.ground.samplesDetail).toHaveLength(371);
  for (const sample of placement.ground.samplesDetail) {
    const p = new Vector3().fromArray(sample.local).applyMatrix4(matrix);
    ray.set(new Vector3(p.x, 50, p.z), new Vector3(0, -1, 0));
    const hit = ray.intersectObjects(surfaces, false)[0]; expect(hit).toBeDefined();
    expect(p.y - hit.point.y).toBeLessThanOrEqual(-.0009);
    expect(p.y - hit.point.y).toBeGreaterThan(-.09);
  }
  const inverse = new Matrix4().fromArray(placement.inverseMatrixColumnMajor);
  expect(new Vector3(.2, 1, -.3).applyMatrix4(matrix).applyMatrix4(inverse).distanceTo(new Vector3(.2, 1, -.3))).toBeLessThan(1e-10);
}, 30_000);
