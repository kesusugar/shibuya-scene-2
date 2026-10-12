// C2a stills: the Core viewpoints, the photo-solved elevated cameras, building bases and the photo-fitted views,
// each before (?ground=off&datum=off = the scene before C2a) and after. Headless SwiftShader: visual check only,
// never a performance figure.
//   node scripts/capture-core.mjs http://127.0.0.1:5181 evidence/c2a [only]
import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';

const [base = 'http://127.0.0.1:5181', out = 'evidence/c2a', only = ''] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
// pose = x,y,z,tx,ty,tz,vfov (plan metres; heights in the common datum, eye = PLATEAU road + 1.6 m)
const P = {
  c01_to_qfront: '6.5,-2.0,1.516,-8,29,12,55', c02_to_crossing: '11.6,-47.0,1.871,6,10,6,55', c03_to_station: '-14.0,25.5,1.719,15,-40,4,55',
  c04_to_crossing: '34.0,7.5,1.617,-10,-15,4,55', c05_to_crossing: '-25.0,29.2,1.725,20,-10,4,55',
  x01_ref_a: '-12.6,-68.2,10.2,0.8,30.7,16.2,52.2', x02_ref_b: '161.9,-201.8,159.6,-5,-18.7,12,15.8',
  top_down: '6.5,-30,190,6.5,-1.9,0,48',
  base_qfront_front: '-15.0,21.0,1.2,-6,30,0.6,50', base_magnet_sw: '25.5,6.0,1.2,33.6,11.3,0.4,50', base_magnet_se: '44.0,4.0,1.2,49.2,9.9,0.3,50',
  kerb_ne_corner: '22.0,8.0,1.3,30,14,0,45',
};
const shots = [];
for (const [name, pose] of Object.entries(P)) {
  const [w, h] = name === 'x01_ref_a' ? [1280, 960] : name === 'x02_ref_b' ? [1280, 964] : [1280, 720];
  shots.push([`${name}_before`, `?time=day&capture&ground=off&datum=off&pose=${pose}`, w, h]);
  shots.push([`${name}_after`, `?time=day&capture&pose=${pose}`, w, h]);
}
for (const t of ['day', 'night']) {
  shots.push([`m027_${t}_before`, `?time=${t}&view=m027&capture&ground=off&datum=off`, 640, 853], [`m027_${t}_after`, `?time=${t}&view=m027&capture`, 640, 853]);
  shots.push([`q032_${t}_before`, `?time=${t}&view=q032&capture&ground=off&datum=off`, 640, 875], [`q032_${t}_after`, `?time=${t}&view=q032&capture`, 640, 875]);
}
shots.push(['night_c01_after', `?time=night&capture&pose=${P.c01_to_qfront}`, 1280, 720]);
shots.push(['isolation_ground_missing', `?time=day&capture&pose=${P.top_down}&groundurl=missing`, 1280, 720]);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const logPath = `${out}/capture_log.json`;
const log = existsSync(logPath) ? JSON.parse(readFileSync(logPath, 'utf8')) : {};
for (const [name, q, w, h] of shots.filter(([n]) => !only || only.split(',').some((o) => n.startsWith(o)))) {
  if (!process.env.FORCE && existsSync(`${out}/${name}.png`) && log[name]) continue;   // resumable
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(base + '/' + q);
  await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 240000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${out}/${name}.png`, timeout: 240000 });
  const v = await page.evaluate(() => ({ ground: window.__viewer.ground, offsets: window.__viewer.offsets, failed: window.__viewer.failed, perf: document.querySelector('#perf')?.textContent, status: document.querySelector('#status')?.textContent }));
  log[name] = { query: q, ...v, errors };
  writeFileSync(logPath, JSON.stringify(log, null, 1));
  console.log(name, JSON.stringify(v.ground), JSON.stringify(v.offsets), errors.length ? 'ERRORS ' + errors.join(' | ') : 'no errors');
  await page.close();
}
await browser.close();
