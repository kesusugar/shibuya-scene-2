import type { WebGLRenderer } from 'three';

/** Rolling frame-time statistics: p50/p95 frame time and FPS over the last N frames, plus renderer counters. */
export class FrameStats {
  private samples: number[] = [];
  private last = performance.now();
  constructor(private size = 240) {}

  tick(): number {
    const now = performance.now();
    const dt = now - this.last;
    this.last = now;
    this.samples.push(dt);
    if (this.samples.length > this.size) this.samples.shift();
    return dt / 1000;
  }

  summary() {
    const s = [...this.samples].sort((a, b) => a - b);
    const q = (p: number) => (s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : 0);
    const mean = s.reduce((a, b) => a + b, 0) / Math.max(1, s.length);
    return { frames: s.length, p50: q(0.5), p95: q(0.95), fps: mean > 0 ? 1000 / mean : 0 };
  }

  report(renderer: WebGLRenderer): string {
    const { frames, p50, p95, fps } = this.summary();
    const info = renderer.info;
    const canvas = renderer.domElement;
    return [
      `FPS ${fps.toFixed(1)}  (${frames}フレーム平均)`,
      `frame p50 ${p50.toFixed(1)} ms / p95 ${p95.toFixed(1)} ms`,
      `draw calls ${info.render.calls}  tris ${(info.render.triangles / 1000).toFixed(0)}k`,
      `geometries ${info.memory.geometries}  textures ${info.memory.textures}`,
      `解像度 ${canvas.width}x${canvas.height}  DPR ${renderer.getPixelRatio().toFixed(2)}`,
    ].join('\n');
  }
}
