import { CanvasTexture, Color, EquirectangularReflectionMapping, Fog, SRGBColorSpace, type Scene, type Texture } from 'three';
import type { TimeOfDay } from './lighting';

/**
 * Sky and aerial perspective (look foundation, Claude 2026-10-14). The flat blue backdrop made every building edge
 * look cut out; a vertical gradient (pale, slightly warm horizon to deeper zenith) and distance fog that fades to the
 * horizon colour give depth. Colours were chosen against the 2025 daytime references (Stream 2025-01, crossing
 * 2025-06): horizon ~#bccddb, 20 degrees up ~#6b9ad2, zenith ~#2f66b4 (eye-level views see mostly the lower 30 degrees). Night keeps a dark blue with a faint city glow at the horizon.
 * ?sky=flat restores the previous flat colour without fog, for comparisons.
 */
export const SKY = {
  day: { zenith: 0x2f66b4, mid: 0x6b9ad2, horizon: 0xbccddb, ground: 0x9aa1a6, fogNear: 300, fogFar: 2200 },
  night: { zenith: 0x061232, mid: 0x0d1d48, horizon: 0x2b2c46, ground: 0x15161c, fogNear: 300, fogFar: 2200 },
} as const;

export function skyTexture(mode: TimeOfDay): Texture | null {
  if (typeof document === 'undefined') return null;
  const c = SKY[mode]; const canvas = document.createElement('canvas'); canvas.width = 4; canvas.height = 256;
  const g = canvas.getContext('2d')!; const grad = g.createLinearGradient(0, 0, 0, 256);
  const hex = (n: number) => `#${n.toString(16).padStart(6, '0')}`;
  grad.addColorStop(0, hex(c.zenith)); grad.addColorStop(0.3, hex(c.mid)); grad.addColorStop(0.47, hex(c.horizon)); grad.addColorStop(0.5, hex(c.horizon)); grad.addColorStop(0.56, hex(c.ground)); grad.addColorStop(1, hex(c.ground));
  g.fillStyle = grad; g.fillRect(0, 0, 4, 256);
  const t = new CanvasTexture(canvas); t.mapping = EquirectangularReflectionMapping; t.colorSpace = SRGBColorSpace;
  return t;
}

export function applyAtmosphere(scene: Scene, mode: TimeOfDay, enabled = true) {
  if (!enabled) { scene.fog = null; return; }
  const c = SKY[mode];
  scene.background = skyTexture(mode) ?? new Color(c.horizon);
  scene.fog = new Fog(c.horizon, c.fogNear, c.fogFar);
}
