import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface TactileSupplementResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** Sidewalk-only tactile supplements; preserve the original tactile asset. */
export async function loadTactileSupplement(loadGlb: (url: string) => Promise<Object3D>, kind: 'extra' | 'links' | 'outer', url = `/street/tactile-${kind}/tactile-${kind}.glb`): Promise<TactileSupplementResult> {
  const root = new Group(); root.name = `street:tactile-${kind}`;
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName(kind === 'extra' ? 'street_tactile' : `street_tactile_${kind}`)) throw new Error('missing tactile supplement mesh');
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
