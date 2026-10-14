import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface TerrainResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** DEM substrate outside the original Core; finished roads remain provisional. */
export async function loadTerrain(loadGlb: (url: string) => Promise<Object3D>, url = '/ground/extension/extension.glb'): Promise<TerrainResult> {
  const root = new Group(); root.name = 'ground:extension';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('ground_fill_extension')) throw new Error('missing terrain mesh');
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
