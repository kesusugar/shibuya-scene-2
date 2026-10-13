import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface TactileResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** Local approaches only. Keep the original terrain as the walk/collision surface. */
export async function loadTactile(loadGlb: (url: string) => Promise<Object3D>, url = '/street/tactile/tactile.glb'): Promise<TactileResult> {
  const root = new Group(); root.name = 'street:tactile';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('street_tactile')) throw new Error('missing tactile mesh');
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
