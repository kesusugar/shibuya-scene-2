// Headless screenshots for visual checks (SwiftShader: NOT a performance measurement).
//   node scripts/capture.mjs http://127.0.0.1:5180 out-dir
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';

const [base = 'http://127.0.0.1:5180', out = 'evidence/g1', only = ''] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const shots = [
  ['day_q032', '?time=day&view=q032&capture', 640, 875],
  ['night_q032', '?time=night&view=q032&capture', 640, 875],
  ['day_orbit', '?time=day&capture', 1280, 720],
  ['night_orbit', '?time=night&capture', 1280, 720],
  ['day_walk', '?time=day&view=walk&capture', 1280, 720],
];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
for (const [name, q, w, h] of shots.filter(([n]) => !only || only.split(',').includes(n))) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(base + '/' + q + (process.env.EXTRA_QUERY ? '&' + process.env.EXTRA_QUERY : ''));
  await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 180000 });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${out}/${name}.png`, timeout: 180000 });
  const hud = await page.textContent('#perf');
  console.log(name, JSON.stringify(await page.evaluate(() => window.__viewer.stats)), errors.length ? 'ERRORS ' + errors.join(' | ') : 'no errors', '\n' + hud);
  await page.close();
}
await browser.close();
