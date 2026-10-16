import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

/** Existing OSM anchor/yaw; vertical fit measured at all 371 lower-rim points on the shipped sidewalk.
 * source/data/scan-placement.json records the measurement and inverse matrix.
 * Source normalization/estimated scale is already baked into the delivered GLB; apply neither again.
 */
export const HACHIKO_SCAN_PLACEMENT = {
  position: [11.568175521259887, 0.3795121888979883, 48.68573220011713] as const,
  yawDegrees: 35,
} as const;

export interface HachikoResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** One complete scan (statue plus all base parts). The former complete asset is not loaded as a fallback. */
export async function loadHachiko(loadGlb: (url: string) => Promise<Object3D>, url = '/street/hachiko/hachiko.glb'): Promise<HachikoResult> {
  const root = new Group(); root.name = 'street:hachiko';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('hachiko_uploaded_scan_candidate_v001')) throw new Error('missing complete hachiko scan');
    let meshes = 0, triangles = 0;
    scene.traverse(o => {
      const m = o as Mesh; if (!m.isMesh) return;
      m.castShadow = true; m.receiveShadow = true; meshes++;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
    });
    if (meshes !== 1 || triangles !== 85_934) throw new Error('unexpected complete scan geometry');
    root.position.set(...HACHIKO_SCAN_PLACEMENT.position);
    root.rotation.y = HACHIKO_SCAN_PLACEMENT.yawDegrees * Math.PI / 180;
    root.add(scene);
    return { ok: true, root, stats: { meshes, triangles } };
  } catch (e) {
    root.clear(); return { ok: false, root, error: String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
