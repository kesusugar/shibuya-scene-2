import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface HachikoResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** Photo-informed statue supplement; retain the original walk surface. */
export async function loadHachiko(loadGlb: (url: string) => Promise<Object3D>, url = '/street/hachiko/hachiko.glb'): Promise<HachikoResult> {
  const root = new Group(); root.name = 'street:hachiko';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('street_hachiko')) throw new Error('missing hachiko mesh');
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
