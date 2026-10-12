import { Group, Mesh, MeshStandardMaterial, PointLight, type Object3D } from 'three';
import { validateBuilding } from './buildings';

/** Every part of street_core.glb v2 (one mesh per material, assets/street/core/source/blender/build_street.py). */
export const STREET_PARTS = [
  'street_concrete', 'street_stair_well', 'street_roof', 'street_panel', 'street_glass', 'street_sign_blue', 'street_sign_white',
  'street_steel', 'street_signal_body', 'street_signal_green', 'street_signal_red', 'street_rail', 'street_lamp_glass',
  'street_tree_bark', 'street_tree_leaves', 'street_tree_leaves_light',
] as const;
const TREE_PARTS = ['street_tree_bark', 'street_tree_leaves', 'street_tree_leaves_light'];
/** Lamp output at night (candela). Generic LED lantern; no photometric data for the Core's lamps. */
export const LAMP_CD = 120;

export interface StreetResult {
  ok: boolean;
  root: Group;
  walkSurfaces: Object3D[];
  lights: PointLight[];
  error?: string;
  stats: { meshes: number; triangles: number };
  setTime(time: 'day' | 'night'): void;
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
    if (!includeTrees) for (const name of TREE_PARTS) {
      const part = scene.getObjectByName(name)!;
      part.parent?.remove(part);
    }
    let meshes = 0, triangles = 0;
    const anchors: Object3D[] = [];
    scene.traverse((o) => {
      if (o.name.startsWith('light_')) anchors.push(o);
      const m = o as Mesh;
      if (!m.isMesh) return;
      meshes++; m.castShadow = !/glass|signal|sign_/.test(m.name); m.receiveShadow = true;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
    });
    root.add(scene);
    const lights = anchors.map((a) => {
      const l = new PointLight(0xffdcae, 0, 32, 2); l.name = a.name; l.castShadow = false;
      a.add(l); return l;
    });
    const glass = (scene.getObjectByName('street_lamp_glass') as Mesh).material as MeshStandardMaterial;
    const setTime = (time: 'day' | 'night') => {
      for (const l of lights) l.intensity = time === 'night' ? LAMP_CD : 0;
      glass.emissive.setHex(0xffdcae); glass.emissiveIntensity = time === 'night' ? 3 : 0;
    };
    setTime('day');
    // Only stair treads and landings are walkable: roofs, rails and crowns never become walking surfaces.
    return { ok: true, root, lights, setTime, walkSurfaces: [scene.getObjectByName('street_concrete')!], stats: { meshes, triangles: Math.round(triangles) } };
  } catch (e) {
    root.clear();
    return { ok: false, root, lights: [], setTime() {}, walkSurfaces: [], error: e instanceof Error ? e.message : String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
