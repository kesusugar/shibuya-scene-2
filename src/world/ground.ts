import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

/** Parts the Core ground GLB must contain (assets/ground/core/source/blender/build_ground.py). */
export const GROUND_PARTS = ['ground_road', 'ground_intersection', 'ground_sidewalk', 'ground_kerb', 'ground_marking', 'ground_fill'] as const;

export interface GroundResult {
  ok: boolean;
  root: Group;
  error?: string;
  missing: string[];
  stats: { meshes: number; triangles: number };
}

/**
 * Loads the Core ground (PLATEAU road surfaces, kerbs, crosswalks) as one independent asset.
 * Never throws: on failure the root is empty and the caller keeps the plain disc, so the buildings still draw.
 * The GLB is already in the common datum (Y = T.P. - 15.000 m), so it is placed at the origin.
 */
export async function loadGround(loadGlb: (url: string) => Promise<Object3D>, url = '/ground/core/ground_core.glb'): Promise<GroundResult> {
  const root = new Group(); root.name = 'ground:core';
  try {
    const scene = await loadGlb(url);
    const problems = validateBuilding(scene);
    if (problems.length) throw new Error(`asset check failed: ${problems.slice(0, 3).join('; ')}`);
    const names = new Set<string>(); let meshes = 0, triangles = 0;
    scene.traverse((o) => {
      names.add(o.name);
      const m = o as Mesh;
      if (!m.isMesh) return;
      meshes++; m.receiveShadow = true; m.castShadow = m.name.startsWith('ground_kerb');
      const pos = m.geometry.getAttribute('position');
      triangles += m.geometry.index ? m.geometry.index.count / 3 : pos.count / 3;
    });
    const missing = GROUND_PARTS.filter((p) => ![...names].some((n) => n === p || n.startsWith(p + '_') || n.startsWith(p + '.')));
    root.add(scene);
    return { ok: true, root, missing, stats: { meshes, triangles: Math.round(triangles) } };
  } catch (e) {
    return { ok: false, root, error: e instanceof Error ? e.message : String(e), missing: [...GROUND_PARTS], stats: { meshes: 0, triangles: 0 } };
  }
}
