import type { WebGLRenderer } from 'three';
import type { FrameStats } from './frame-stats';

export interface BenchmarkResult {
  date: string; userAgent: string; gpu: string; quality: string; time: string; view: string;
  seconds: number; frames: number; fps: number; p50_ms: number; p95_ms: number;
  drawCalls: number; triangles: number; canvas: string; dpr: number;
}

/** Unmasked GPU name where the browser exposes it (it may not); recorded with every measurement. */
export function gpuName(renderer: WebGLRenderer): string {
  const gl = renderer.getContext();
  const ext = gl.getExtension('WEBGL_debug_renderer_info');
  return ext ? String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : String(gl.getParameter(gl.RENDERER));
}

/** Records frame statistics for `seconds` and returns a JSON-able result the owner can paste back. */
export function runBenchmark(stats: FrameStats, renderer: WebGLRenderer, meta: { quality: string; time: string; view: string }, seconds = 30): Promise<BenchmarkResult> {
  stats.reset(seconds * 240);
  return new Promise((resolve) => {
    setTimeout(() => {
      const s = stats.summary(); const info = renderer.info; const c = renderer.domElement;
      resolve({
        date: new Date().toISOString(), userAgent: navigator.userAgent, gpu: gpuName(renderer), ...meta, seconds,
        frames: s.frames, fps: +s.fps.toFixed(1), p50_ms: +s.p50.toFixed(1), p95_ms: +s.p95.toFixed(1),
        drawCalls: info.render.calls, triangles: info.render.triangles, canvas: `${c.width}x${c.height}`, dpr: renderer.getPixelRatio(),
      });
    }, seconds * 1000);
  });
}
