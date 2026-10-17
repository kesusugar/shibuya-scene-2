import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface RearTreeResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

interface Placement {
  position: [number, number, number];
  yaw_deg: number;
  uniform_scale: number;
}

/** One photo-identified tree behind the statue; stone enclosure remains a separate item. */
export async function loadRearTree(
  loadGlb: (url: string) => Promise<Object3D>,
  loadJson: (url: string) => Promise<unknown>,
  modelUrl = '/street/hachiko-rear-tree/hachiko-rear-tree.glb',
): Promise<RearTreeResult> {
  const root = new Group(); root.name = 'street:hachiko-rear-tree';
  try {
    const [scene, raw] = await Promise.all([loadGlb(modelUrl), loadJson('/street/hachiko-rear-tree/placement.json')]);
    const placement = raw as Placement;
    const problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('hachiko_rear_tree_candidate_v001')) throw new Error('missing rear tree model');
    if (!Array.isArray(placement.position) || placement.position.length !== 3 ||
        !placement.position.every(Number.isFinite) || !Number.isFinite(placement.yaw_deg) ||
        placement.uniform_scale !== 1) throw new Error('invalid rear tree placement');
    scene.position.set(...placement.position);
    scene.rotation.y = placement.yaw_deg * Math.PI / 180;
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
