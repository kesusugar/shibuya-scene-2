import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';

const base = 'assets/buildings/daiichi-kangin/';
const json = (path: string) => JSON.parse(readFileSync(path, 'utf8'));

it('replaces the Daiichi C model exactly once without duplicating its C shell', () => {
  const input = json('assets/context/core/source/data/context_input.json');
  const stats = json('assets/context/core/source/data/context_stats.json');
  for (const c of [input, stats]) {
    expect(c.buildings.some((b: { id: string }) => b.id === 'way/114755219')).toBe(false);
    expect(c.excluded.filter((b: { id: string }) => b.id === 'way/114755219')).toHaveLength(1);
  }
  const ground = json(base+'source/data/stats.json');
  expect(ground.pavement_samples.length).toBeGreaterThan(30);
  expect(ground.pavement_samples.every((p: { tp: number }) => Number.isFinite(p.tp))).toBe(true);
  expect(json(base+'web/viewer.json').groundElevationTP).toBe(15);
});

it('retains original roof vertices and exports architectural glazing without advertising textures', async () => {
  const source = json(base+'source/data/plateau.json');
  const root = (await new NodeIO().read(base+'web/daiichi-kangin.glb')).getRoot();
  const roof: Vector3[] = [];
  for (const node of root.listNodes()) {
    const matrix = new Matrix4().fromArray(node.getWorldMatrix());
    for (const primitive of node.getMesh()?.listPrimitives() ?? []) {
      const name = primitive.getMaterial()!.getName();
      expect(primitive.getMaterial()!.getBaseColorTexture()).toBeNull();
      if (name !== 'dk_roof') continue;
      const pos = primitive.getAttribute('POSITION')!;
      for (let i = 0; i < pos.getCount(); i++) roof.push(new Vector3().fromArray(pos.getElement(i, [])).applyMatrix4(matrix));
    }
  }
  for (const s of source.surfaces.filter((s: { kind: string }) => s.kind !== 'WallSurface')) {
    for (const p of s.ring) expect(roof.some(v => v.distanceTo(new Vector3(p[0], p[2], -p[1])) < .002)).toBe(true);
  }
  const names = root.listMaterials().map(m => m.getName());
  expect(names).toContain('dk_glass'); expect(names).toContain('dk_infill'); expect(names).toContain('dk_sign_back');
  expect(roof.length).toBeGreaterThan(50);
});

it('keeps the east glazing visible in front of the retained source shell from the street', async () => {
  const root = (await new NodeIO().read(base+'web/daiichi-kangin.glb')).getRoot();
  const material = new MeshBasicMaterial({ side: DoubleSide });
  const meshes: Mesh[] = [];
  try {
    for (const node of root.listNodes()) for (const primitive of node.getMesh()?.listPrimitives() ?? []) {
      const matrix = new Matrix4().fromArray(node.getWorldMatrix());
      const pos = primitive.getAttribute('POSITION')!, idx = primitive.getIndices();
      const points: number[] = [];
      for (let i = 0; i < (idx?.getCount() ?? pos.getCount()); i++) {
        const p = new Vector3().fromArray(pos.getElement(idx ? idx.getScalar(i) : i, [])).applyMatrix4(matrix);
        points.push(p.x, p.y, p.z);
      }
      const geo = new BufferGeometry(); geo.setAttribute('position', new Float32BufferAttribute(points, 3));
      const mesh = new Mesh(geo, material); mesh.name = primitive.getMaterial()!.getName(); meshes.push(mesh);
    }
    const layout = json(base+'source/data/layout.json');
    const east = layout.facades[1], u = 8.5/12;
    const tp = json(base+'source/data/plateau.json').ground_tp-15;
    const x = east.a[0]+(east.b[0]-east.a[0])*u+east.normal[0]*.09;
    const y = east.a[1]+(east.b[1]-east.a[1])*u+east.normal[1]*.09;
    const origin = new Vector3(-28, 4, 8);
    const target = new Vector3(x, tp+26.1, -y);
    expect(new Raycaster(origin, target.sub(origin).normalize()).intersectObjects(meshes, false)[0]?.object.name).toBe('dk_glass');
  } finally { for (const mesh of meshes) mesh.geometry.dispose(); material.dispose(); }
});
