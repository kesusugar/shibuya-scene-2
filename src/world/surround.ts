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
    const [scene, shrubs, seating] = await Promise.all([loadGlb(url),
      loadGlb('/street/hachiko-surround/shrubs.glb'), loadGlb('/street/hachiko-surround/seating.glb')]);
    for (const model of [scene, shrubs, seating]) {
      const problems = validateBuilding(model);
      if (problems.length) throw new Error(problems.join(', '));
    }
    if (!scene.getObjectByName('street_surround')) throw new Error('missing surround mesh');
    // The shrubs and retained soil/rock already contain WORLD coordinates.
    // Only the local seating pack receives the equipment transform (not statue yaw).
    const equipment = new Group(); equipment.name = 'surround:seating';
    equipment.position.set(11.568175521259887, 0, 48.68573220011713);
    equipment.rotation.y = 35 * Math.PI / 180;
    for (const [name, height] of [['current_left_statue_local_origin', .4710693359375],
      ['current_right_statue_local_origin', .4155540466308594]] as const) {
      const child = seating.getObjectByName(name);
      if (!child) throw new Error(`missing seating root: ${name}`);
      child.position.y = height;
    }
    equipment.add(seating);
    root.add(scene, shrubs, equipment);
    let meshes = 0, triangles = 0;
    root.traverse(o => {
      const m = o as Mesh; if (!m.isMesh) return;
      m.castShadow = true; m.receiveShadow = true; meshes++;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
    });
    return { ok: true, root, stats: { meshes, triangles } };
  } catch (e) {
    root.clear(); return { ok: false, root, error: String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
