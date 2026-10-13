// C2b fix: identical cameras for the Codex v1 street (before) and the v2 street (after).
// node scripts/capture-street-fix.mjs <base url> <out dir>   (VIEWS=a,b limits the views; resumable)
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
const [base, out] = process.argv.slice(2);
const views = {
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
    await page.goto(`${base}/?capture&${v.q}${process.env.EXTRA ? `&${process.env.EXTRA}` : ""}`);
    await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 300000 });
    await page.waitForTimeout(2500);
    const state = await page.evaluate(() => ({ street: window.__viewer.street, context: window.__viewer.context, stats: window.__viewer.stats, failed: window.__viewer.failed, status: document.querySelector('#status').textContent }));
    await page.screenshot({ path: `${out}/${name}.png`, timeout: 300000 });
    log[name] = { ...v, state, errors }; writeFileSync(logPath, JSON.stringify(log, null, 2));
    assert.deepEqual(errors, []); assert.equal(state.status, ''); assert.deepEqual(state.failed, []); assert.equal(state.context.ok, true); assert.equal(state.street.ok, true);
    console.log(name, errors.length ? errors : 'ok'); await page.close();
  }
} finally { await browser.close(); }
