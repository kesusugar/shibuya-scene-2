// C3a: for every photograph with a solved camera, a beauty render and a class pass at the photo's aspect ratio.
// look-metrics.py then compares photo and render class by class. Headless SwiftShader: appearance only, never FPS.
//   node scripts/capture-look.mjs http://127.0.0.1:5182 evidence/c3a/<label> [extra query]
import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const [base = 'http://127.0.0.1:5182', out = 'evidence/c3a/now', extra = ''] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
export const VIEWS = {
  m027: { q: 'time=day&view=m027', w: 640, h: 853 },                                            // 2025-09-01 13:18, CC0
  q032: { q: 'time=day&view=q032', w: 640, h: 875 },                                            // 2018-10-30, CC BY-SA 4.0
  refa: { q: 'time=day&pose=-12.6,-68.2,10.2,0.8,30.7,16.2,52.2', w: 640, h: 480 },             // 2010, CC BY 2.0
  refb: { q: 'time=night&pose=161.9,-201.8,159.6,-5,-18.7,12,15.8', w: 640, h: 482 },           // 2024 night, CC0
};
function validateFrame(name, row) {
  assert.ok(row?.state?.viewer, `${name}: no validated capture log; use FORCE=1 or a new output directory`);
  assert.deepEqual(row.errors, [], `${name}: browser/network errors`);
  assert.deepEqual(row.state.viewer.failed, [], `${name}: failed buildings`);
  assert.deepEqual(Object.keys(row.state.viewer.stats).sort(), [...(row.expectedBuildings ?? ['qfront', 'magnet', 'eiraku'])].sort());
  assert.equal(row.state.viewer.ground.ok, true, `${name}: ground failed`);
  assert.deepEqual(row.state.viewer.ground.missing, []);
  for (const s of Object.values(row.state.viewer.stats)) assert.deepEqual(s.layerErrors, []);
  assert.equal(row.state.status, '', `${name}: viewer reported a fallback`);
}
const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const logFile = `${out}/capture_log.json`;
const log = existsSync(logFile) ? JSON.parse(readFileSync(logFile, 'utf8')) : {};
const only = (process.env.VIEWS || '').split(',').filter(Boolean);
try {
for (const [name, v] of Object.entries(VIEWS).filter(([n]) => !only.length || only.includes(n))) {
  for (const pass of (process.env.PASSES || 'beauty,class').split(',')) {
    const file = `${out}/${name}_${pass}.png`;
    if (existsSync(file) && !process.env.FORCE) {
      validateFrame(`${name}_${pass}`, log[`${name}_${pass}`]);
      console.log(name, pass, 'skipped (validated saved evidence)');
      continue;
    }
    const page = await browser.newPage({ viewport: { width: v.w, height: v.h } });
    // The viewer has no favicon. Avoid an unrelated browser-generated 404 in the evidence log.
    await page.route('**/favicon.ico', (route) => route.fulfill({ status: 204 }));
    const errors = [];
    page.on('response', (r) => { if (r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`); });
    page.on('requestfailed', (r) => errors.push(`${r.url()}: ${r.failure()?.errorText}`));
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    const q = `/?${v.q}&capture${pass === 'class' ? '&pass=class' : ''}${extra ? '&' + extra : ''}`;
    await page.goto(base + q);
    await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 240000 });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: file, timeout: 240000 });
    const state = await page.evaluate(() => ({ viewer: window.__viewer, status: document.querySelector('#status')?.textContent }));
    log[`${name}_${pass}`] = { query: q, errors, state, expectedBuildings: (new URLSearchParams(q.split('?')[1]).get('buildings') ?? 'qfront,magnet,eiraku,west-block,ekimae,station-concourse').split(',').filter((id) => new URLSearchParams(q.split('?')[1]).get('context') !== 'nostation' || id !== 'station-concourse'),
      browser: browser.version(), executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || 'playwright bundled',
      perf: await page.evaluate(() => document.querySelector('#perf')?.textContent) };
    // Persist each completed frame even if a later frame fails.
    writeFileSync(`${out}/capture_log.json`, JSON.stringify(log, null, 1));
    validateFrame(`${name}_${pass}`, log[`${name}_${pass}`]);
    console.log(name, pass, errors.length ? 'ERRORS ' + errors.join(' | ') : 'ok');
    await page.close();
  }
}
writeFileSync(logFile, JSON.stringify(log, null, 1));
} finally {
  await browser.close();
}
