import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding } from './buildings';

export interface FacilitiesResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number };
}

/** OSM-positioned facility supplement with explicitly estimated standard shapes. */
export async function loadFacilities(loadGlb: (url: string) => Promise<Object3D>, url = '/street/plaza-facilities/plaza-facilities.glb'): Promise<FacilitiesResult> {
  const root = new Group(); root.name = 'street:facilities';
  try {
    const scene = await loadGlb(url), problems = validateBuilding(scene);
    if (problems.length) throw new Error(problems.join(', '));
    if (!scene.getObjectByName('street_plaza_facilities_housing')) throw new Error('missing facility mesh');
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
