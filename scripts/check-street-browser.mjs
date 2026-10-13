// Failure isolation, real-light state and walking height; frozen build to avoid dev hot reload.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
const [base = 'http://127.0.0.1:5184', out = 'evidence/c2b/browser'] = process.argv.slice(2);
mkdirSync(out, { recursive: true }); const log = {};
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
for (const [name, query] of Object.entries({ street_missing: 'streeturl=missing', projected_missing: 'street=projected&projectedurl=missing', walk: 'view=walk', lamps: 'street=projected&time=night', stream_projection: 'street=projected&streetref=stream2025' })) {
  const page = await browser.newPage({ viewport: name === 'stream_projection' ? { width: 720, height: 956 } : { width: 320, height: 240 } }); const errors = [], httpErrors = [], missingResponses = [];
  await page.route('**/favicon.ico', (r) => r.fulfill({ status: 204 }));
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('response', (r) => { if (r.status() >= 400) httpErrors.push(r.url()); if (r.url().endsWith('/missing.glb')) missingResponses.push({ status: r.status(), type: r.headers()['content-type'] }); });
  await page.goto(`${base}/?${query}`);
  await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 240000 });
  const result = await page.evaluate(() => ({ viewer: window.__viewer, status: document.querySelector('#status').textContent,
    notice: document.querySelector('#provisional').textContent, camera: window.__viewer.cameraPos(), ground: window.__viewer.groundUnderCamera() }));
  assert.deepEqual(errors, []); assert.deepEqual(result.viewer.failed, []);
  assert.equal(Object.keys(result.viewer.stats).length, 6); assert.equal(result.viewer.ground.ok, true);
  if (name === 'street_missing') { assert.equal(result.viewer.street.ok, false); assert.ok(result.status.includes('街路設備')); assert.ok(result.viewer.street.error || result.viewer.projected.error); assert.equal(missingResponses.length, 1); assert.ok(missingResponses[0].status >= 400 || missingResponses[0].type.includes('text/html')); }
  if (name === 'projected_missing') { assert.equal(result.viewer.projected.ok, false); assert.equal(result.viewer.street.ok, true); assert.ok(result.status.includes('仮配置')); assert.ok(result.viewer.street.error || result.viewer.projected.error); assert.equal(missingResponses.length, 1); assert.ok(missingResponses[0].status >= 400 || missingResponses[0].type.includes('text/html')); }
  if (name === 'walk') {
    assert.ok(Math.abs(result.camera[1] - result.ground - 1.6) < 1e-6);
    assert.equal(result.status, ''); assert.equal(httpErrors.length, 0);
  }
  if (name === 'lamps') {
    assert.equal(result.viewer.projected.groundEmissive, 0);
    assert.ok(result.viewer.projected.lamps.every((l) => l.intensity === 1800));
    assert.ok(result.notice.includes('仮配置')); assert.equal(result.status, ''); assert.equal(httpErrors.length, 0);
  }
  if (name === 'stream_projection') {
    const data = JSON.parse(readFileSync('assets/street/core/source/data/photo_projections.json', 'utf8'));
    result.projectionChecks = [];
    for (const row of data.observations.filter((r) => r.point)) {
      const px = await page.evaluate((p) => window.__viewer.projectPlan(p), [...row.point, row.anchor_tp - 15]);
      const expected = row.px.map((v) => v * 0.8);
      const error = Math.hypot(px[0] - expected[0], px[1] - expected[1]);
      assert.ok(error < 0.15, `${row.id}: camera/export projection inconsistent (${error} px)`);
      result.projectionChecks.push({ id: row.id, expected, rendered: px, error_px: error });
    }
  }
  log[name] = { query, ...result, errors, httpErrors, missingResponses, browser: browser.version() };
  writeFileSync(`${out}/checks.json`, JSON.stringify(log, null, 2)); console.log(name, 'ok'); await page.close();
}
} finally { await browser.close(); }
