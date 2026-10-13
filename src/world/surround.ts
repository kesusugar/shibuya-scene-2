import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface SurroundResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** Photo-informed planter supplement; retain the original walk surface. */
export async function loadSurround(loadGlb: (url: string) => Promise<Object3D>, url = '/street/hachiko-surround/hachiko-surround.glb'): Promise<SurroundResult> {
  const root = new Group(); root.name = 'street:surround';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('street_surround')) throw new Error('missing surround mesh');
    let meshes = 0, triangles = 0;
    scene.traverse(o => {
      const m = o as Mesh; if (!m.isMesh) return;
      m.castShadow = true; m.receiveShadow = true; meshes++;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
    });
    root.add(scene);
    return { ok: true, root, stats: { meshes, triangles } };
  } catch (e) {
    root.clear(); return { ok: false, root, error: String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
