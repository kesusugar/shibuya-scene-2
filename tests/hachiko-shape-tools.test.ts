import { it, expect } from 'vitest';
import { execFileSync } from 'node:child_process';
import { readFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';

const live = 'assets/street/hachiko/web/hachiko.glb';
const sha = () => createHash('sha256').update(readFileSync(live)).digest('hex');
function run(script: string) {
  const output = join(mkdtempSync(join(tmpdir(), 'hachiko-shape-check-')), 'nested', 'result.json');
  execFileSync(process.execPath, ['scripts/' + script, output], { encoding: 'utf8' });
  return JSON.parse(readFileSync(output, 'utf8'));
}
it('reruns the historical plinth projection against the pinned legacy asset, leaving the live scan intact', () => {
  const before = sha(), report = run('check-hachiko-shape.mjs');
  expect(report.model_reference.scope).toBe('historical_handcrafted_model_only');
  expect(report.model_reference.path).toBe('assets/street/hachiko/source/legacy/hachiko.glb');
  expect(report.model_reference.current_scan_evaluated).toBe(false);
  expect(report.final_model_aspect).toBeCloseTo(0.7189116580222507, 12);
  expect(sha()).toBe(before);
});
it('measures the historical dog only, rather than the complete scan and its pedestal', () => {
  const before = sha(), report = run('check-surround-shape.mjs');
  expect(report.model_reference.path).toBe('assets/street/hachiko/source/legacy/hachiko.glb');
  expect(report.model_reference.current_scan_evaluated).toBe(false);
  expect(report.model_world_ranges_m.dog[0]).toBeCloseTo(1.8622074574232101, 10);
  expect(report.model_world_ranges_m.dog[1]).toBeCloseTo(2.849950850009918, 10);
  expect(Number.isFinite(report.final_world_gap_over_dog_height)).toBe(true);
  expect(sha()).toBe(before);
});
