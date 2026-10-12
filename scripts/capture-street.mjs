// Repeatable C2b comparisons: identical camera, one category or lighting variable per stage.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
const [base = 'http://127.0.0.1:5183', out = 'evidence/c2b/projected'] = process.argv.slice(2);
const cases = {
  stream_before: { query: 'street=off&streetref=stream2025&time=day', w: 720, h: 956 },
  stream_known: { query: 'streetref=stream2025&time=day', w: 720, h: 956 },
  stream_projected: { query: 'street=projected&streetref=stream2025&time=day', w: 720, h: 956 },
  overview_known: { query: 'pose=60,-85,55,6.5,-2,0,52&time=day', w: 800, h: 600 },
  overview_projected: { query: 'street=projected&pose=60,-85,55,6.5,-2,0,52&time=day', w: 800, h: 600 },
  night_zero: { query: 'street=projected&lamps=off&look=nightGround:0&time=night&pose=161.9,-201.8,159.6,-5,-18.7,12,15.8', w: 640, h: 482 },
  night_emissive: { query: 'street=projected&lamps=off&look=nightGround:0.5&time=night&pose=161.9,-201.8,159.6,-5,-18.7,12,15.8', w: 640, h: 482 },
  night_lamps: { query: 'street=projected&look=nightGround:0&time=night&pose=161.9,-201.8,159.6,-5,-18.7,12,15.8', w: 640, h: 482 },
};
mkdirSync(out, { recursive: true }); const log = existsSync(`${out}/capture_log.json`) ? JSON.parse(readFileSync(`${out}/capture_log.json`, 'utf8')) : {};
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
for (const [name, v] of Object.entries(cases)) {
  if (process.env.VIEWS && !process.env.VIEWS.split(',').includes(name)) continue;
  const page = await browser.newPage({ viewport: { width: v.w, height: v.h } }); const errors = [];
  await page.route('**/favicon.ico', (r) => r.fulfill({ status: 204 }));
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('response', (r) => { if (r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`); });
  page.on('requestfailed', (r) => errors.push(`${r.url()}: ${r.failure()?.errorText}`));
  await page.goto(`${base}/?capture&${v.query}`);
  await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 240000 });
  await page.waitForTimeout(2500);
  const state = await page.evaluate(() => ({ viewer: window.__viewer, status: document.querySelector('#status').textContent, notice: document.querySelector('#provisional').textContent }));
  assert.deepEqual(errors, []); assert.equal(state.status, ''); assert.deepEqual(state.viewer.failed, []);
  assert.equal(state.viewer.ground.ok, true);
  if (v.query.includes('street=projected')) {
    assert.equal(state.viewer.projected.ok, true); assert.equal(state.viewer.projected.status, 'experimental_only');
    assert.equal(state.viewer.projected.lamps.length, 3);
    assert.ok(state.notice.includes('仮配置'));
    assert.ok(state.viewer.projected.lamps.every((l) => l.intensity === (name === 'night_lamps' ? 1800 : 0)));
  }
  await page.screenshot({ path: `${out}/${name}.png`, timeout: 240000 });
  log[name] = { ...v, state, errors, browser: browser.version() }; writeFileSync(`${out}/capture_log.json`, JSON.stringify(log, null, 2));
  console.log(name, 'ok'); await page.close();
}
} finally { await browser.close(); }
