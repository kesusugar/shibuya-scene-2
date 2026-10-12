import { Color, Mesh, MeshBasicMaterial, type Material, type Object3D, type Texture } from 'three';
import type { EmissiveTable } from './buildings';

/**
 * Material classes shared by every asset in the Core. The look pass (C3a) tunes the WebGL appearance per class, not
 * per photo or per building, and the class pass (?pass=class) paints them flat so a render can be compared with a
 * photograph class by class (scripts/look-metrics.py).
 */
export type LookClass = 'glass' | 'sign' | 'interior' | 'wall' | 'road' | 'sidewalk' | 'kerb' | 'marking' | 'fill';

/** Flat colours for the class pass (sRGB, exact values are what look-metrics.py reads back). */
export const CLASS_COLORS: Record<LookClass, number> = {
  glass: 0x0000ff, sign: 0xffff00, interior: 0xff00ff, wall: 0xff0000,
  road: 0x00ff00, sidewalk: 0x00ffff, kerb: 0x808000, marking: 0xffffff, fill: 0x008080,
};

const SIGN = /(letters|logo|screen|led|banner|wrap|sign|poster|q_bar|tsutaya_face|sb_green|menu|amaguri|acom|lake|aiful|_t$|mark|label|qs_eye)/;
const INTERIOR = /(interior|shop_light|ceil_light|ceiling|goods|shelf|books|pendant|floor|skin|hair|blind|wood$|lamp_head|cloth|denim)/;

/** Class of one material. Ground parts are named by the ground generator; buildings use their emissive table kinds. */
export function classify(material: Material, meshName: string, table?: EmissiveTable, inSignLayer = false): LookClass {
  const n = material.name || '';
  if (meshName.startsWith('ground_') || n.startsWith('ground_')) {
    if (n.includes('marking') || meshName.startsWith('ground_marking')) return 'marking';
    if (n.includes('kerb') || meshName.startsWith('ground_kerb')) return 'kerb';
    if (n.includes('fill') || meshName.startsWith('ground_fill')) return 'fill';
    if (n.includes('sidewalk') || n.includes('island') || meshName.startsWith('ground_sidewalk')) return 'sidewalk';
    return 'road';
  }
  const kind = table?.[n]?.kind;
  if (kind === 'glass' || /glass/.test(n)) return 'glass';
  if (kind === 'led' || inSignLayer || SIGN.test(n)) return 'sign';
  if (INTERIOR.test(n)) return 'interior';
  return 'wall';
}

/** Paints every mesh with its class colour (unlit, not tone mapped). QA only: the scene is not restored afterwards. */
export function applyClassPass(root: Object3D, table?: EmissiveTable) {
  const cache = new Map<LookClass, MeshBasicMaterial>();
  const mat = (c: LookClass) => {
    if (!cache.has(c)) cache.set(c, new MeshBasicMaterial({ color: new Color(CLASS_COLORS[c]), toneMapped: false }));
    return cache.get(c)!;
  };
  root.traverse((o) => {
    const mesh = o as Mesh;
    if (!mesh.isMesh) return;
    let p: Object3D | null = mesh; let inSign = false;
    while (p) { if (/:signs/.test(p.name)) inSign = true; p = p.parent; }
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    const out = mats.map((m) => mat(classify(m, mesh.name, table, inSign)));
    mesh.material = Array.isArray(mesh.material) ? out : out[0];
    mesh.castShadow = mesh.receiveShadow = false;
  });
}

/**
 * The common WebGL look (C3a): one set of per-class parameters for every asset, day and night. Values are chosen by
 * scripts/look-metrics.py over all photographed views at once (docs/core/C3A_REPORT.md), never for one photograph.
 * Every value can be overridden for experiments with ?look=key:value,key:value.
 */
export interface LookParams {
  dayExposure: number; nightExposure: number;
  glassEnv: number; wallEnv: number;           // envMapIntensity per class (scene.environmentIntensity applies on top)
  road: number; sidewalk: number;              // linear albedo of asphalt / paving (flat grey, C3 material pass later)
  nightGround: number;                         // night: emissive on the ground as albedo x this (stands in for street lights until C2b)
  nightSign: number;                           // night: multiplier on the baked emissive strength of signs and screens
}
export const LOOK_DEFAULT: LookParams = {
  dayExposure: 0.85, nightExposure: 1.35, glassEnv: 1.6, wallEnv: 0.5, road: 0.045, sidewalk: 0.30,
  // Provisional REF-B fit only: restore 0 when C2b adds actual street lights (see C3A_REPORT.md).
  nightGround: 0.5, nightSign: 1.0,
};
export function parseLook(q: string | null, base: LookParams = LOOK_DEFAULT): LookParams {
  const out = { ...base };
  for (const kv of (q ?? '').split(',').filter(Boolean)) {
    const [k, v] = kv.split(':'); const n = Number(v);
    if (k in out && Number.isFinite(n)) (out as Record<string, number>)[k] = n;
  }
  return out;
}

/** Applies the look to one loaded asset. Call after applyEmissive (sign scaling multiplies the table strength). */
export function applyLook(root: Object3D, mode: 'day' | 'night', look: LookParams, table?: EmissiveTable, env?: { map: Texture | null; intensity: number }) {
  root.traverse((o) => {
    const mesh = o as Mesh;
    if (!mesh.isMesh) return;
    let p: Object3D | null = mesh; let inSign = false;
    while (p) { if (/:signs/.test(p.name)) inSign = true; p = p.parent; }
    for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
      const std = m as MeshStandardLike;
      if (!('envMapIntensity' in std)) continue;
      const c = classify(m, mesh.name, table, inSign);
      // three.js only honours envMapIntensity when the material has its own envMap (otherwise scene.environmentIntensity
      // applies to all): glass and walls get the scene's map, scaled so 1.0 reproduces the uniform look
      if ((c === 'glass' || c === 'wall') && env) {
        std.envMap = env.map; std.envMapIntensity = (c === 'glass' ? look.glassEnv : look.wallEnv) * env.intensity; std.needsUpdate = true;
      }
      else if ((c === 'road' || c === 'sidewalk') && !/island/.test(m.name)) {
        const a = c === 'road' ? look.road : look.sidewalk;
        if (!std.userData.lookBase) std.userData.lookBase = std.color.clone();
        const base = std.userData.lookBase as Color; const lum = (base.r + base.g + base.b) / 3 || 1;
        std.color.setRGB((base.r / lum) * a, (base.g / lum) * a, (base.b / lum) * a);   // keep the hue, set the albedo
        std.emissive.copy(std.color).multiplyScalar(mode === 'night' ? look.nightGround : 0);
        std.emissiveIntensity = 1;
      } else if (c === 'sign' && mode === 'night') std.emissiveIntensity *= look.nightSign;
    }
  });
}
type MeshStandardLike = Material & { envMap: Texture | null; envMapIntensity: number; color: Color; emissive: Color; emissiveIntensity: number };
