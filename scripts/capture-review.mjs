// Claude review of PR #12-#36: identical cameras before/after each fix. Default quality (no q=), one browser per view.
// node scripts/capture-review.mjs <base> <out>   VIEWS=a,b  FORCE=1  EXTRA=query
import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
const [base, out] = process.argv.slice(2);
export const views = {
  entry: { q: 'time=day', w: 1000, h: 700 },                                   // initial screen (QFRONT framing)
  entry_night: { q: 'time=night', w: 1000, h: 700 },
  stream: { q: 'time=day&streetref=stream2025', w: 720, h: 956 },
  m027: { q: 'time=day&view=m027', w: 640, h: 853 },
  west_eye: { q: 'time=day&pose=10,-8,1.9,-30,22,12,60', w: 1000, h: 700 },  // crossing centre -> west block
  ekimae_eye: { q: 'time=day&pose=-10,10,1.9,40,-40,14,60', w: 1000, h: 700 }, // -> ekimae / station side
  hachiko_close: { q: 'time=day&pose=38,-36,1.7,49,-45,1.2,50', w: 1000, h: 700 },
  plaza: { q: 'time=day&pose=20,-10,6,55,-50,0,60', w: 1000, h: 700 },
  concourse: { q: 'time=day&pose=2,-12,1.7,-22,-80,12,58', w: 960, h: 720 },   // same direction as crossing_2025.jpg (2025-06)
  statue_front: { q: 'time=day&pose=9.274,-45.409,1.9,11.568,-48.686,1.4,44', w: 750, h: 900 },   // Codex PR #28-#30 camera
  statue_side: { q: 'time=day&pose=7,-52,2.2,11.568,-48.686,1.4,44', w: 900, h: 750 },
  b109: { q: 'time=day&pose=-75,-20,70,-155,10,25,55', w: 900, h: 750 },   // Codex PR #35 camera
  b109_street: { q: 'time=day&pose=-110,-10,1.8,-150,6,25,60', w: 750, h: 900 },
  gate: { q: 'time=day&pose=-22,22,1.8,-27.5,36,4.6,58', w: 900, h: 700 },
  plaza_se: { q: 'time=day&pose=2,-34,1.7,32,-64,6,62', w: 1000, h: 700 },   // plaza towards the station side (same direction as hachiko.jpg, 2025-11)
  station_front: { q: 'time=day&pose=10,-5,1.9,70,-40,8,62', w: 1000, h: 700 },
};
if (base) {
  mkdirSync(out, { recursive: true });
  const logPath = `${out}/capture_log.json`; const log = existsSync(logPath) ? JSON.parse(readFileSync(logPath, 'utf8')) : {};
  for (const [name, v] of Object.entries(views)) {
    if (process.env.VIEWS && !process.env.VIEWS.split(',').includes(name)) continue;
    if (!process.env.FORCE && existsSync(`${out}/${name}.png`)) continue;
    const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
    try {
      const page = await browser.newPage({ viewport: { width: v.w, height: v.h } }); const errors = [];
      page.on('pageerror', (e) => errors.push(e.message));
      page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
      await page.goto(`${base}/?capture&${v.q}${process.env.EXTRA ? '&' + process.env.EXTRA : ''}`);
      await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 400000 });
      await page.waitForTimeout(3000);
      const status = await page.evaluate(() => document.querySelector('#status')?.textContent ?? '');
      await page.screenshot({ path: `${out}/${name}.png`, timeout: 400000 });
      log[name] = { ...v, extra: process.env.EXTRA ?? '', status, errors }; writeFileSync(logPath, JSON.stringify(log, null, 2));
      console.log(name, errors.length || status ? JSON.stringify({ errors, status }).slice(0, 300) : 'ok');
    } finally { await browser.close(); }
  }
}
