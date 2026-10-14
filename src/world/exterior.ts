import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';
export interface ExteriorResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number; tiles: number };
}
/** Finished street prototypes outside the protected Core footprint. */
export async function loadExterior(loadGlb: (url: string) => Promise<Object3D>, prefix = '/ground'): Promise<ExteriorResult> {
  const root = new Group(); root.name = 'ground:exterior';
  try {
    const tiles = await Promise.all(['west','middle','east'].map(async id => {
      const scene = await loadGlb(`${prefix}/exterior-${id}/exterior-${id}.glb`);
      const problems = validateBuilding(scene);
      if (problems.length) throw new Error(`${id}: ${problems.join(', ')}`);
      for (const name of ['ground_road','ground_sidewalk']) if (!scene.getObjectByName(name)) throw new Error(`${id}: missing ${name}`);
      return scene;
    }));
    let meshes = 0, triangles = 0;
    for (const tile of tiles) { tile.traverse(o => {
      const m = o as Mesh; if (!m.isMesh) return;
      m.castShadow = false; m.receiveShadow = true; meshes++;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count)/3;
    }); root.add(tile); }
    return {ok:true, root, stats:{meshes,triangles,tiles:tiles.length}};
  } catch(e) { root.clear(); return {ok:false,root,error:String(e),stats:{meshes:0,triangles:0,tiles:0}}; }
}

/** Keep the original fill as fallback unless the complete replacement ground is ready. */
export function replaceProvisionalFill(root: Object3D, replacementsReady: boolean): boolean {
  if (!replacementsReady) return false;
  const fill = root.getObjectByName('ground_fill');
  if (!fill) return false;
  fill.removeFromParent();
  return true;
}
