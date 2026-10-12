// C3a: for every photograph with a solved camera, a beauty render and a class pass at the photo's aspect ratio.
// look-metrics.py then compares photo and render class by class. Headless SwiftShader: appearance only, never FPS.
//   node scripts/capture-look.mjs http://127.0.0.1:5182 evidence/c3a/<label> [extra query]
import { chromium } from 'playwright';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';

const [base = 'http://127.0.0.1:5182', out = 'evidence/c3a/now', extra = ''] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
export const VIEWS = {
  m027: { q: 'time=day&view=m027', w: 640, h: 853 },                                            // 2025-09-01 13:18, CC0
  q032: { q: 'time=day&view=q032', w: 640, h: 875 },                                            // 2018-10-30, CC BY-SA 4.0
  refa: { q: 'time=day&pose=-12.6,-68.2,10.2,0.8,30.7,16.2,52.2', w: 640, h: 480 },             // 2010, CC BY 2.0
  refb: { q: 'time=night&pose=161.9,-201.8,159.6,-5,-18.7,12,15.8', w: 640, h: 482 },           // 2024 night, CC0
};
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const log = {};
const only = (process.env.VIEWS || '').split(',').filter(Boolean);
for (const [name, v] of Object.entries(VIEWS).filter(([n]) => !only.length || only.includes(n))) {
  for (const pass of (process.env.PASSES || 'beauty,class').split(',')) {
    const file = `${out}/${name}_${pass}.png`;
    if (existsSync(file) && !process.env.FORCE) continue;
    const page = await browser.newPage({ viewport: { width: v.w, height: v.h } });
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    const q = `/?${v.q}&capture${pass === 'class' ? '&pass=class' : ''}${extra ? '&' + extra : ''}`;
    await page.goto(base + q);
    await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 240000 });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: file, timeout: 240000 });
    log[`${name}_${pass}`] = { query: q, errors, perf: await page.evaluate(() => document.querySelector('#perf')?.textContent) };
    console.log(name, pass, errors.length ? 'ERRORS ' + errors.join(' | ') : 'ok');
    await page.close();
  }
}
await browser.close();
writeFileSync(`${out}/capture_log_${Date.now()}.json`, JSON.stringify(log, null, 1));
