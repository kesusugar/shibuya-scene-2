import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface MemorialResult {
  ok: boolean;
  root: Group;
  error?: string;
  stats: { meshes: number; triangles: number };
}

interface MemorialPlacement {
  position: [number, number, number];
  yaw_deg: number;
  uniform_scale: number;
}

/** Replaces only the former blank stone panel beside the adopted statue. */
export async function loadMemorial(
  loadGlb: (url: string) => Promise<Object3D>,
  loadJson: (url: string) => Promise<unknown>,
  modelUrl = '/street/hachiko-memorial/hachiko-memorial.glb',
): Promise<MemorialResult> {
  const root = new Group(); root.name = 'street:memorial';
  try {
    const [scene, raw] = await Promise.all([loadGlb(modelUrl), loadJson('/street/hachiko-memorial/placement.json')]);
    const placement = raw as MemorialPlacement;
    if (validateBuilding(scene).length) throw new Error('invalid memorial GLB');
    if (!scene.getObjectByName('hachiko_memorial_bilingual_v001')) throw new Error('missing memorial model');
    if (!Array.isArray(placement.position) || placement.position.length !== 3 ||
        !placement.position.every(Number.isFinite) || !Number.isFinite(placement.yaw_deg) ||
        placement.uniform_scale !== 1) throw new Error('invalid memorial placement');
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
