// C2a QA: in walk mode the eye must stay 1.6 m above the Core ground while walking over kerbs and slopes.
//   node scripts/walk-check.mjs http://127.0.0.1:5181 evidence/c2a/walk_check.json
import { chromium } from 'playwright';
import { writeFileSync } from 'node:fs';
const [base = 'http://127.0.0.1:5181', out = 'evidence/c2a/walk_check.json'] = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
await page.goto(base + '/?time=day&view=walk&capture');
await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 240000 });
const samples = [];
for (const key of ['KeyW', 'KeyD', 'KeyW', 'KeyA', 'KeyS']) {
  await page.keyboard.down(key);
  for (let i = 0; i < 6; i++) {
    await page.waitForTimeout(700);
    samples.push(await page.evaluate((k) => { const p = window.__viewer.cameraPos(); return { key: k, x: +p[0].toFixed(2), y: +p[1].toFixed(3), z: +p[2].toFixed(2), ground: +window.__viewer.groundUnderCamera().toFixed(3) }; }, key));
  }
  await page.keyboard.up(key);
}
await browser.close();
const eye = samples.map((s) => +(s.y - s.ground).toFixed(3));
const res = { samples, eye_min: Math.min(...eye), eye_max: Math.max(...eye), ground_min: Math.min(...samples.map((s) => s.ground)), ground_max: Math.max(...samples.map((s) => s.ground)),
  moved_m: +Math.hypot(samples.at(-1).x - samples[0].x, samples.at(-1).z - samples[0].z).toFixed(2) };
writeFileSync(out, JSON.stringify(res, null, 1));
console.log(JSON.stringify({ eye_min: res.eye_min, eye_max: res.eye_max, ground_min: res.ground_min, ground_max: res.ground_max, n: samples.length }));
