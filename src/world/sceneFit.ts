import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface SceneFitResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** Swap visible geometry only after every requested part has loaded; original collision roots stay intact. */
export function applySceneFitReplacements(result: SceneFitResult, originals: { facilities?: Object3D; plaza?: Object3D; kiosk?: Object3D }) {
  if (!result.ok) return;
  for (const [name, original] of [['lottery',originals.facilities],['finish',originals.plaza],['a8',originals.kiosk]] as const) {
    if (original && result.root.children.some(o => o.name === `fit:${name}`)) original.visible = false;
  }
}

/** Assets already fitted in metres to the scene datum; do not apply another world transform. */
export async function loadSceneFit(loadGlb: (url: string) => Promise<Object3D>, names: string[]): Promise<SceneFitResult> {
  const root = new Group(); root.name = 'street:hachiko-fit';
  try {
    const parts = await Promise.all(names.map(name => loadGlb(`/street/hachiko-fit/${name}.glb`)));
    let meshes = 0, triangles = 0;
    for (const [i, part] of parts.entries()) {
      const errors = validateBuilding(part, names[i] === 'fence' ? 0.1 : 1); if (errors.length) throw Error(`${names[i]}: ${errors.join(', ')}`);
      part.traverse(o => { const m = o as Mesh; if (!m.isMesh) return;
        meshes++; triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
        m.receiveShadow = true;
      });
      part.name = `fit:${names[i]}`; root.add(part);
    }
    return { ok: true, root, stats: { meshes, triangles } };
  } catch (error) {
    root.clear(); return { ok: false, root, error: String(error), stats: { meshes: 0, triangles: 0 } };
  }
}
