import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export const STREET_PARTS = ['street_roof', 'street_steel', 'street_concrete', 'street_tree_bark', 'street_tree_leaves'] as const;
export interface StreetResult {
  ok: boolean;
  root: Group;
  walkSurfaces: Object3D[];
  error?: string;
  stats: { meshes: number; triangles: number };
}

/** Independent asset in the same T.P. datum as the ground. Failure must not hide buildings or ground. */
export async function loadStreet(loadGlb: (url: string) => Promise<Object3D>, url = '/street/core/street_core.glb', includeTrees = true): Promise<StreetResult> {
  const root = new Group(); root.name = 'street:core';
  try {
    const scene = await loadGlb(url);
    const problems = validateBuilding(scene);
    if (problems.length) throw new Error(`asset check failed: ${problems.slice(0, 3).join('; ')}`);
    const missing = STREET_PARTS.filter((name) => !scene.getObjectByName(name));
    if (missing.length) throw new Error(`missing street parts: ${missing.join(', ')}`);
    if (!includeTrees) for (const name of ['street_tree_bark', 'street_tree_leaves']) {
      const part = scene.getObjectByName(name)!;
      part.parent?.remove(part);
    }
    let meshes = 0, triangles = 0;
    scene.traverse((o) => {
      const m = o as Mesh;
      if (!m.isMesh) return;
      meshes++; m.castShadow = m.receiveShadow = true;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
    });
    root.add(scene);
    // Roofs and foliage must never become walking surfaces: ground rays start above the entire scene.
    return { ok: true, root, walkSurfaces: [scene.getObjectByName('street_concrete')!], stats: { meshes, triangles: Math.round(triangles) } };
  } catch (e) {
    return { ok: false, root, walkSurfaces: [], error: e instanceof Error ? e.message : String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
