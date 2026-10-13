import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface PlazaResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** Photo-informed planter supplement; retain the original walk surface. */
export async function loadPlaza(loadGlb: (url: string) => Promise<Object3D>, url = '/street/plaza-finish/plaza-finish.glb'): Promise<PlazaResult> {
  const root = new Group(); root.name = 'street:plaza';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('plaza_finish')) throw new Error('missing plaza mesh');
    let meshes = 0, triangles = 0;
    scene.traverse(o => {
      const m = o as Mesh; if (!m.isMesh) return;
      m.castShadow = false; m.receiveShadow = true; meshes++;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
    });
    root.add(scene);
    return { ok: true, root, stats: { meshes, triangles } };
  } catch (e) {
    root.clear(); return { ok: false, root, error: String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
