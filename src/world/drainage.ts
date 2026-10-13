import { Box3, Group, Mesh, Vector3, type Object3D } from 'three';

export interface DrainageResult {
  ok: boolean; root: Group; error?: string; stats: { meshes: number; triangles: number };
}
/** Small road details do not use building-size validation or replace the walk surface. */
export async function loadDrainage(loadGlb: (url: string) => Promise<Object3D>, url = '/street/drainage/drainage.glb'): Promise<DrainageResult> {
  const root = new Group(); root.name = 'street:drainage';
  try {
    const scene = await loadGlb(url);
    if (!scene.getObjectByName('street_drainage')) throw new Error('missing road cover mesh');
    let meshes = 0, triangles = 0;
    scene.traverse(o => {
      const m = o as Mesh; if (!m.isMesh) return;
      const p = m.geometry.getAttribute('position');
      if (!p?.count) throw new Error('empty cover geometry');
      for (let i = 0; i < p.count; i++) if (![p.getX(i), p.getY(i), p.getZ(i)].every(Number.isFinite)) throw new Error('non-finite cover geometry');
      m.castShadow = false; m.receiveShadow = true; meshes++;
      triangles += (m.geometry.index?.count ?? p.count) / 3;
    });
    const size = new Box3().setFromObject(scene).getSize(new Vector3());
    if (!meshes || !triangles || ![size.x, size.y, size.z].every(Number.isFinite) || Math.max(size.x, size.y, size.z) < .1 || Math.max(size.x, size.y, size.z) > 5) throw new Error('invalid cover extent');
    root.add(scene); return { ok: true, root, stats: { meshes, triangles } };
  } catch (e) {
    root.clear(); return { ok: false, root, error: String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
