// C2b fix: identical cameras for the Codex v1 street (before) and the v2 street (after).
// node scripts/capture-street-fix.mjs <base url> <out dir>   (VIEWS=a,b limits the views; resumable)
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
const [base, out] = process.argv.slice(2);
const views = {
  tactile_network: { q: 'time=day&pose=25,-33,2,21.2,-24.7,.2,65', w: 900, h: 675 },
  tactile_close: { q: 'time=day&pose=22,-18,1.9,22.9,-13.1,.2,65', w: 900, h: 675 },
  plaza: { q: 'time=day&pose=27,-32,2.3,18,-18,.4,65', w: 900, h: 675 },
  plaza_night: { q: 'time=night&pose=27,-32,2.3,18,-18,.4,65', w: 900, h: 675 },
  entry_left: { q: "time=day&pose=20.134654,-33.508250,25.255800,32.406007,45.484403,24,55", w: 1000, h: 750 },
  entry_right: { q: "time=day&pose=20.134654,-33.508250,25.255800,-42.139314,16.615380,24,55", w: 1000, h: 750 },
  paving: { q: "time=day&pose=-15,25,1.9,-8,19,.3,65", w: 900, h: 675 },
  paving_night: { q: "time=night&pose=-15,25,1.9,-8,19,.3,65", w: 900, h: 675 },
  gate: { q: "time=day&pose=-14,9,2,-27,36,4,50", w: 900, h: 675 },
  gate_night: { q: "time=night&pose=-14,9,2,-27,36,4,50", w: 900, h: 675 },
  daiichi_front: { q: "time=day&pose=-28,-8,4,-82,31,21,58", w: 900, h: 675 },
  entry: { q: "time=day", w: 1000, h: 750 },
  entry_night: { q: "time=night", w: 1000, h: 750 },
  center_front: { q: "time=day&pose=-6,12,4,-45,61,16,48", w: 900, h: 675 },
  ginza_hall_night: { q: 'time=night&pose=148,-65,15.2,190,-51,16.3,65', w: 900, h: 675 },
  ginza_hall: { q: 'time=day&pose=148,-65,15.2,190,-51,16.3,65', w: 900, h: 675 },
  station_viaduct: { q: 'time=day&pose=12,-48,13,32,-90,9,55', w: 900, h: 675 },
  station_service: { q: 'time=day&pose=9,-38,18,35,-64,7,55', w: 900, h: 675 },
  station_concourse_night: { q: 'time=night&pose=-15,-44,2,-16,-74,8,55', w: 900, h: 600 },
  station_platform: { q: 'time=day&pose=62.0467,-23.8225,7.89,44,-56,10,58', w: 900, h: 675 },
  station_concourse: { q: 'time=day&pose=-15,-44,2,-16,-74,8,55', w: 900, h: 600 },
  m027: { q: 'time=day&view=m027', w: 640, h: 853 },
  stream: { q: 'time=day&streetref=stream2025', w: 720, h: 956 },
  overview: { q: 'time=day&pose=60,-85,55,6.5,-2,0,52', w: 800, h: 600 },
  ne_corner: { q: 'time=day&pose=-6,-14,1.9,24,12,3,60', w: 800, h: 600 },          // eye level, SW island to the NE corner
  sw_island: { q: 'time=day&pose=12,24,1.9,-26,-8,3,60', w: 800, h: 600 },          // eye level, from the north crosswalk
  hachiko: { q: 'time=day&pose=30,-24,1.9,-10,8,4,62', w: 800, h: 600 },            // eye level, station side looking NW
  night: { q: 'time=night&pose=161.9,-201.8,159.6,-5,-18.7,12,15.8', w: 640, h: 482 },
  night_street: { q: 'time=night&pose=12,24,1.9,-26,-8,3,60', w: 800, h: 600 },
};
mkdirSync(out, { recursive: true });
const logPath = `${out}/capture_log.json`; const log = existsSync(logPath) ? JSON.parse(readFileSync(logPath, 'utf8')) : {};
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  for (const [name, v] of Object.entries(views)) {
    if (process.env.VIEWS && !process.env.VIEWS.split(',').includes(name)) continue;
    if (!process.env.FORCE && existsSync(`${out}/${name}.png`)) continue;
    const page = await browser.newPage({ viewport: { width: v.w, height: v.h } }); const errors = [];
    await page.route('**/favicon.ico', (r) => r.fulfill({ status: 204 }));
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('response', (r) => { if (r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`); });
    page.on('requestfailed', (r) => errors.push(`${r.url()}: ${r.failure()?.errorText}`));
    await page.goto(`${base}/?capture&${v.q}${process.env.EXTRA ? `&${process.env.EXTRA}` : ""}`);
    await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 300000 });
    await page.waitForTimeout(2500);
    const state = await page.evaluate(() => ({ tactile: window.__viewer.tactile, ground: window.__viewer.ground, street: window.__viewer.street, context: window.__viewer.context, stats: window.__viewer.stats, failed: window.__viewer.failed, status: document.querySelector('#status').textContent }));
    await page.screenshot({ path: `${out}/${name}.png`, timeout: 300000 });
    log[name] = { ...v, state, errors, capturedAt: new Date().toISOString(), cameraPos: await page.evaluate(() => window.__viewer.cameraPos()) }; writeFileSync(logPath, JSON.stringify(log, null, 2));
    assert.deepEqual(errors, []); assert.equal(state.status, ''); assert.deepEqual(state.failed, []); assert.equal(state.context.ok, true); assert.equal(state.street.ok, true); if (process.env.EXTRA?.includes('tactile=off')) assert.equal(state.tactile, 'off'); else assert.equal(state.tactile.ok, true); assert.equal(state.ground.ok, true); assert.deepEqual(state.ground.missing, []);
    for (const asset of Object.values(state.stats)) assert.deepEqual(asset.layerErrors, []);
    console.log(name, errors.length ? errors : 'ok'); await page.close();
  }
} finally { await browser.close(); }
