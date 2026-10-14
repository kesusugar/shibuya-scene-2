import { DataTexture, LinearFilter, LinearMipmapLinearFilter, Mesh, RepeatWrapping, RGBAFormat, type Material, type Object3D } from 'three';
import { classify, type LookClass } from './look';

/**
 * Surface detail (look foundation, Claude 2026-10-14): world-space variation on the flat-coloured surfaces, so
 * asphalt, paving and walls stop reading as single-colour planes. It needs no UVs (PLATEAU-derived meshes have none):
 * a procedural noise texture (own work, seeded) is sampled with the fragment's world position.
 * - road: large mottling, fine grain, sparse darker repair patches, slightly glossier wheel tracks are not modelled
 * - sidewalk / kerb / fill (no own texture): mottling, fine grain and 0.30 m paving joints (sidewalk only)
 * - wall (buildings without hand-made materials): soft vertical weathering streaks and a darker base band
 * The mean multiplier stays close to 1, so the per-class albedo chosen in C3a (look.ts) is kept on average.
 */
export type DetailKind = 'road' | 'paving' | 'plain' | 'wall';

/** Seeded tileable value noise: R = large mottle, G = fine grain, B = sparse patch mask, A = vertical streaks. */
export function makeDetailTexture(size = 256, seed = 7): DataTexture {
  let s = seed >>> 0;
  const rand = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const grid = (n: number) => { const g = new Float32Array(n * n); for (let i = 0; i < g.length; i++) g[i] = rand(); return g; };
  const sample = (g: Float32Array, n: number, x: number, y: number) => {       // bilinear, wraps -> tileable
    const fx = (x * n) / size, fy = (y * n) / size, x0 = Math.floor(fx), y0 = Math.floor(fy), tx = fx - x0, ty = fy - y0;
    const at = (i: number, j: number) => g[((j % n) + n) % n * n + (((i % n) + n) % n)];
    const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
    return (at(x0, y0) * (1 - sx) + at(x0 + 1, y0) * sx) * (1 - sy) + (at(x0, y0 + 1) * (1 - sx) + at(x0 + 1, y0 + 1) * sx) * sy;
  };
  const g4 = grid(4), g8 = grid(8), g16 = grid(16), g64 = grid(64), g128 = grid(128), gp = grid(12), gs = grid(32);
  const data = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const large = 0.5 * sample(g4, 4, x, y) + 0.3 * sample(g8, 8, x, y) + 0.2 * sample(g16, 16, x, y);
    const fine = 0.6 * sample(g128, 128, x, y) + 0.4 * sample(g64, 64, x, y);
    const patch = sample(gp, 12, x, y) > 0.78 ? 1 : 0;
    // streaks: noise stretched along y (32 columns, 4 rows)
    const streak = 0.7 * sample(gs, 32, x, y / 8) + 0.3 * sample(g64, 64, x, y / 4);
    const i = (y * size + x) * 4;
    data[i] = large * 255; data[i + 1] = fine * 255; data[i + 2] = patch * 255; data[i + 3] = streak * 255;
  }
  const t = new DataTexture(data, size, size, RGBAFormat);
  t.wrapS = t.wrapT = RepeatWrapping; t.magFilter = LinearFilter; t.minFilter = LinearMipmapLinearFilter; t.generateMipmaps = true;
  t.needsUpdate = true; t.name = 'surface_detail';
  return t;
}

const KIND_ID: Record<DetailKind, number> = { road: 0, paving: 1, plain: 2, wall: 3 };

export function detailKind(c: LookClass, material: Material): DetailKind | null {
  if ((material as { map?: unknown }).map) return null;                // already has its own texture (pavers, signs)
  if (c === 'road') return 'road';
  if (c === 'sidewalk') return /island/.test(material.name) ? 'plain' : 'paving';
  if (c === 'kerb' || c === 'fill') return 'plain';
  if (c === 'wall') return 'wall';
  return null;
}

/** Adds the world-space detail to one material (idempotent). Exported for tests. */
export function addDetail(material: Material, kind: DetailKind, tex: DataTexture) {
  const m = material as Material & { userData: Record<string, unknown> };
  if (m.userData.surfaceDetail) return;
  m.userData.surfaceDetail = kind;
  m.onBeforeCompile = (shader) => {
    shader.uniforms.uDetail = { value: tex };
    shader.uniforms.uDetailKind = { value: KIND_ID[kind] };
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vDetailWorld;')
      .replace('#include <project_vertex>', `#include <project_vertex>
  {
    vec4 dw = vec4(transformed, 1.0);
    #ifdef USE_INSTANCING
      dw = instanceMatrix * dw;
    #endif
    vDetailWorld = (modelMatrix * dw).xyz;
  }`);
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vDetailWorld;\nuniform sampler2D uDetail;\nuniform int uDetailKind;\nfloat detailRough = 1.0;')
      .replace('#include <map_fragment>', `#include <map_fragment>
  {
    vec3 w = vDetailWorld;
    float k = 1.0;
    if (uDetailKind == 3) {
      // walls: vertical streaks (sampled along the wall plane, both horizontal axes) and a darker 0.8 m base band
      float s = texture2D(uDetail, vec2((w.x + w.z) / 23.0, w.y / 40.0)).a;
      float big = texture2D(uDetail, vec2((w.x - w.z) / 61.0, w.y / 37.0)).r;
      k = mix(0.86, 1.06, s) * mix(0.93, 1.05, big);
      k *= mix(0.84, 1.0, smoothstep(-0.4, 1.4, w.y));
    } else {
      vec4 a = texture2D(uDetail, w.xz / 37.0);
      vec4 b = texture2D(uDetail, w.xz / 3.1);
      k = mix(0.84, 1.12, a.r) * mix(0.9, 1.08, b.g);
      if (uDetailKind == 0) {
        // asphalt: sparse, slightly darker repair patches and a glossier fine grain
        float p = texture2D(uDetail, w.xz / 19.0 + vec2(0.37, 0.11)).b;
        k *= mix(1.0, 0.8, p);
        detailRough = mix(0.88, 1.06, b.g);
      }
      if (uDetailKind == 1) {
        // 0.30 m paving joints
        vec2 g = abs(fract(w.xz / 0.30) - 0.5);
        float joint = 1.0 - smoothstep(0.455, 0.49, max(g.x, g.y));
        k *= mix(0.8, 1.0, joint);
      }
    }
    diffuseColor.rgb *= k;
  }`)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = clamp(roughnessFactor * detailRough, 0.04, 1.0);');
  };
  m.customProgramCacheKey = () => `surface-detail-${kind}`;
  m.needsUpdate = true;
}

/**
 * Applies the detail to every eligible material under root. Hand-made hero assets (QFRONT, MAGNET, Eiraku) are left
 * untouched by the caller; class pass materials (MeshBasicMaterial) are skipped by classify/envMapIntensity check.
 */
export function applySurfaceDetail(root: Object3D, tex: DataTexture, kinds: DetailKind[] = ['road', 'paving', 'plain', 'wall']): number {
  let n = 0;
  root.traverse((o) => {
    const mesh = o as Mesh;
    if (!mesh.isMesh) return;
    let p: Object3D | null = mesh; let inSign = false;
    while (p) { if (/:signs/.test(p.name)) inSign = true; p = p.parent; }
    for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
      if (!('roughness' in m)) continue;
      const kind = detailKind(classify(m, mesh.name, undefined, inSign), m);
      if (kind && kinds.includes(kind)) { addDetail(m, kind, tex); n++; }
    }
  });
  return n;
}
