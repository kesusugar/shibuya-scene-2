import { Color, Group, Mesh, MeshStandardMaterial, SRGBColorSpace, TextureLoader, type Object3D, type Texture } from 'three';
import { validateBuilding } from './buildings';

/**
 * C-level context of the Core (assets/context/core): PLATEAU 2025 LOD2 shells of every building without its own asset,
 * with shared procedural facade tiles. A stand-in, never a finished building: A/B assets replace it one building at a
 * time (the generator excludes buildings that have an asset). Groups: 'core' and 'station' (station side, shape still
 * to be checked against 2025-10 photographs; ?context=nostation hides it).
 */
export const CONTEXT_TINTS: Record<string, number> = {
  ctx_wall_ribbon_a: 0xc9ccce, ctx_wall_ribbon_b: 0xa7b0b8, ctx_wall_punched_a: 0xd8cfbf, ctx_wall_punched_b: 0xb3aca3,
};
export interface ContextResult {
  ok: boolean;
  root: Group;
  error?: string;
  stats: { meshes: number; triangles: number };
  setTime(time: 'day' | 'night'): void;
}

export async function loadContext(loadGlb: (url: string) => Promise<Object3D>, url = '/context/core/context_core.glb', showStation = true,
  loadTexture: (url: string) => Promise<Texture> = (u) => new TextureLoader().loadAsync(u)): Promise<ContextResult> {
  const root = new Group(); root.name = 'context:core';
  try {
    const scene = await loadGlb(url);
    const problems = validateBuilding(scene);
    if (problems.length) throw new Error(`asset check failed: ${problems.slice(0, 3).join('; ')}`);
    if (!scene.getObjectByName('core__ctx_roof')) throw new Error('missing core__ctx_roof');
    const emit: Record<string, Texture | null> = { ribbon: null, punched: null };
    await Promise.all(Object.keys(emit).map(async (k) => {
      try { const t = await loadTexture(url.replace(/[^/]+$/, `facade_${k}_emit.png`)); t.colorSpace = SRGBColorSpace; t.flipY = false; emit[k] = t; } catch { emit[k] = null; }   // flipY false: glTF UV convention
    }));
    let meshes = 0, triangles = 0; const walls: MeshStandardMaterial[] = [];
    scene.traverse((o) => {
      const m = o as Mesh; if (!m.isMesh) return;
      if (!showStation && m.name.startsWith('station__')) { m.visible = false; return; }
      meshes++; m.castShadow = m.receiveShadow = true;
      triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
      const mat = m.material as MeshStandardMaterial;
      const tint = CONTEXT_TINTS[mat.name];
      if (tint !== undefined) { mat.color = new Color(tint); walls.push(mat); }
    });
    root.add(scene);
    const setTime = (time: 'day' | 'night') => {
      for (const w of walls) {
        const t = emit[w.name.includes('ribbon') ? 'ribbon' : 'punched'];
        w.emissiveMap = time === 'night' ? t : null; w.emissive.setHex(time === 'night' && t ? 0xffd7a0 : 0x000000);
        w.emissiveIntensity = time === 'night' ? 0.55 : 0; w.needsUpdate = true;
      }
    };
    setTime('day');
    return { ok: true, root, setTime, stats: { meshes, triangles: Math.round(triangles) } };
  } catch (e) {
    root.clear();
    return { ok: false, root, setTime() {}, error: e instanceof Error ? e.message : String(e), stats: { meshes: 0, triangles: 0 } };
  }
}
