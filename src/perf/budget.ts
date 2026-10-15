/**
 * Performance budget of the Core (C3a). FPS cannot be measured in the cloud workspace (no GPU), so every asset is held
 * to counts that do not depend on the machine: triangles, draw primitives (one draw call per primitive per pass) and
 * download size. tests/budget.test.ts checks the shipped assets against these numbers on every run; the owner's PC
 * measures real FPS once per milestone (?bench=auto).
 *
 * Fidelity levels follow the owner's A/B/C plan: A = photo-matched hero, B = main form, walls and signs,
 * C = PLATEAU form with shared materials.
 */
export const LEVEL_BUDGET = {
  A: { triangles: 450_000, primitives: 120, bytes: 9_000_000 },
  B: { triangles: 120_000, primitives: 40, bytes: 3_000_000 },
  C: { triangles: 20_000, primitives: 6, bytes: 400_000 },
  ground: { triangles: 120_000, primitives: 12, bytes: 4_000_000 },
  // the C-level pack of every Core building without its own asset (PLATEAU shells, shared materials), counted as one
  context: { triangles: 150_000, primitives: 16, bytes: 6_000_000 },
} as const;
export type Level = keyof typeof LEVEL_BUDGET;

/** Level of every shipped asset (an era layer counts with its building). */
export const ASSET_LEVEL: Record<string, Level> = {'street/props':'B','street/tactile-outer':'B','ground/exterior-west':'ground','ground/exterior-middle':'ground','ground/exterior-east':'ground','mark-city': 'B', 'shibuya109': 'B', 'takagi': 'B', 'bic-camera': 'B', 'cine-tower': 'B', 'east-mixeduse': 'B', 'hikarie': 'B', 'parco': 'B', 'stream': 'B', 'sakura-stage': 'B',  'street/tactile-extra':'B','street/tactile-links':'B', 'plaza-kiosk':'B', 'street/plaza-facilities':'B', 'station-southeast': 'B', 'ground/extension': 'ground','center244': 'B', 'quattro': 'B', 'scramble-square': 'B', 'fukuras': 'B',  qfront: 'A', magnet: 'A', eiraku: 'B', 'west-block': 'B', ekimae: 'B', 'station-concourse': 'B', 'station-north': 'B', 'station-service': 'B', 'station-west-viaduct': 'B', 'ginza-canopy': 'B', 'daiichi-kangin': 'B', 'center-gai-gate': 'B', 'ground/core': 'ground', 'street/core': 'B', 'street/tactile': 'B', 'street/drainage': 'B', 'street/hachiko': 'B', 'street/hachiko-surround': 'B', 'street/plaza-finish': 'B', 'context/core': 'context' };

/**
 * Whole-scene budget for the Core v1 (everything loaded at once, before shadows double the draws). Chosen so that a
 * 16 GB PC with an integrated GPU has headroom; to be confirmed by the owner's measurement at the C4 freeze.
 * About 25 Tier 1 buildings at mixed levels (6 A, 12 B, 7 C) plus ground and street furniture fit inside it.
 */
export const SCENE_BUDGET = { triangles: 4_500_000, primitives: 1_400, bytes: 90_000_000 };
