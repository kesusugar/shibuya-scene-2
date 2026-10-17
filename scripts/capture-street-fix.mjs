// C2b fix: identical cameras for the Codex v1 street (before) and the v2 street (after).
// node scripts/capture-street-fix.mjs <base url> <out dir>   (VIEWS=a,b limits the views; resumable)
import assert from 'node:assert/strict';
import { reuseKey } from './capture-reuse.mjs';
import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
const [base, out] = process.argv.slice(2);
const views = {
  statue_station: {q:'time=day&pose=20.5,-46,2.05,11.568,-48.686,1.5,52',w:1000,h:750},
  statue_station_oblique: {q:'time=day&pose=18,-54,2.0,11.568,-48.686,1.4,55',w:1000,h:750},
  statue_top: {q:'time=day&pose=11.568,-48.686,16,11.568,-48.685,.3,48',w:1000,h:1000},
  shrubs_close: {q:'time=day&pose=15,-53,1.6,12.5,-50,1.2,52',w:1000,h:750},
  box_accessories: {q:'time=day&pose=21.5,-38,2.8,24.3,-41.1,2.8,48',w:1000,h:750},
  box_stage5_night: {q:'time=night&pose=16,-58,4,25.5,-46.6,1.1,62',w:1000,h:750},
  contents_front: {q:'time=day&pose=21.15,-47.315,2.289,25.9,-46.57,1.69,52',w:1200,h:900},
  contents_oblique: {q:'time=day&pose=21.7,-49.3,2.35,25.9,-46.57,1.69,58',w:1200,h:900},
  contents_night: {q:'time=night&pose=21.15,-47.315,2.289,25.9,-46.57,1.69,52',w:1200,h:900},
  contents_tkts: {q:'time=day&pose=21.8,-51.5,2.25,26.5,-50.5,1.8,55',w:1100,h:850},
  contents_shelves: {q:'time=day&pose=20.8,-43.3,2.25,25.8,-43.0,1.9,55',w:1100,h:850},
  stage5_station: {q:'time=day&pose=36,-28,14,16,-49,1,58',w:1200,h:800},
  capture_default: {q:'time=day',w:800,h:600},
  fit_route_top: {q:'time=day&pose=35,-46,35,35,-46,0,58',w:1000,h:900},
  fit_tree_back: {q:'time=day&pose=3,-40,3,7.4,-45.5,.7,58',w:1000,h:750},
  fit_a8_roof: {q:'time=day&pose=42,-56,10,35,-46,3,58',w:1000,h:750},
  fit_route_join: {q:'time=day&pose=20,-33,2,23.7,-35,.2,50',w:1000,h:750},
  fit_overview: {q:'time=day&pose=-8,-66,20,24,-48,1.5,58',w:1200,h:800},
  fit_whole: {q:'time=day&pose=-4,-37,19,24,-49,1,58',w:1200,h:800},
  fit_whole_night: {q:'time=night&pose=-4,-37,19,24,-49,1,58',w:1200,h:800},
  fit_louvre_front: {q:'time=day&pose=35,-53,5,51.2,-55.1,4,50',w:1100,h:750},
  fit_louvre_oblique: {q:'time=day&pose=37,-65,6,51.2,-55.1,4,55',w:1100,h:750},
  fit_enclosure: {q:'time=day&pose=8,-51,2.2,7.95,-46.3,.9,58',w:1000,h:750},
  fit_enclosure_feet: {q:'time=day&pose=8,-49,1.1,7.95,-46.3,.5,58',w:1000,h:750},
  fit_paving: {q:'time=day&pose=12,-43,7,11.568,-48.686,.4,55',w:1000,h:750},
  fit_tactile: {q:'time=day&pose=37,-58,4,35.5,-52,.4,55',w:1000,h:750},
  fit_fence: {q:'time=day&pose=6,-48,1.8,2.2,-46,.6,52',w:1000,h:750},
  fit_a8_front: {q:'time=day&pose=33,-56,2.1,35.8,-51,1.8,57',w:1000,h:750},
  fit_a8_oblique: {q:'time=day&pose=45,-59,4,35,-47,1.8,58',w:1000,h:750},
  fit_a8_feet: {q:'time=day&pose=33,-54,1,35.8,-51,.4,55',w:1000,h:750},
  fit_lottery_front: {q:'time=day&pose=9,-54,2.1,10.9,-62.25,1.9,50',w:1000,h:750},
  fit_lottery_oblique: {q:'time=day&pose=2,-56,3,10.9,-62.25,1.6,52',w:1000,h:750},
  fit_lottery_feet: {q:'time=day&pose=10,-58,1,10.9,-61.5,.65,50',w:1000,h:750},
  st2_whole: {q:'time=day&pose=7,7,12,47,-24,3.2,55',w:1100,h:750},
  st2_front: {q:'time=day&pose=26,-20,3,48,-23,2.7,48',w:1100,h:750},
  st2_oblique: {q:'time=day&pose=34,-35,3.4,48,-23,2.5,55',w:1100,h:750},
  st2_feet: {q:'time=day&pose=39,-22,.8,47,-23,.4,55',w:1200,h:750},
  st1_whole: {q:'time=day&pose=128,-1,14,90,-24,2.6,55',w:1100,h:750},
  st1_front: {q:'time=day&pose=114,-18,3.5,90,-25,2.4,48',w:1100,h:750},
  st1_oblique: {q:'time=day&pose=108,-41,4.8,90,-25,2.4,55',w:1100,h:750},
  st1_detail: {q:'time=day&pose=102,-21.5,3.4,90,-25,2.7,48',w:1200,h:750},
  box_lightbox: {q:'time=day&pose=20,-50.8,2.25,25,-50.1,3.03,40',w:1100,h:650},
  box_signs: {q:'time=day&pose=18,-48,4.1,25.1,-46.7,3.45,50',w:1400,h:600},
  box_clock: {q:'time=day&pose=23,-36,2.1,24.25,-41.15,1.75,48',w:900,h:900},
  box_whole: {q:'time=day&pose=7,-29,10,25.5,-46.6,1.4,58',w:1000,h:750},
  box_front: {q:'time=day&pose=12,-48.7,2.4,25.5,-46.6,1.4,62',w:1000,h:750},
  box_oblique: {q:'time=day&pose=16,-58,4,25.5,-46.6,1.1,62',w:1000,h:750},
  box_feet: {q:'time=day&pose=20,-48,1.15,24.7,-48,.45,62',w:1000,h:750},
  exterior_walk: {q:'time=day&pose=-107,12,3.6,-148,10,17,65',w:1000,h:750},
  exterior_markcity: {q:'time=day&pose=-90,-90,150,-125,-130,0,65',w:1000,h:750},
  b109: {q:'time=day&pose=-75,-20,70,-155,10,25,55',w:900,h:750},
  markcity: {q:'time=day&pose=-5,-150,150,-165,-130,50,65',w:900,h:750},
  takagi: {q:'time=day&pose=-26,30,75,-73,100,25,55',w:900,h:750},
  bic: {q:'time=day&pose=-55,-60,60,-88,-20,15,55',w:900,h:750},
  cine: {q:'time=day&pose=-75,-12,90,-140,-50,30,55',w:900,h:750},
  mixed: {q:'time=day&pose=50,-20,70,90,23,25,55',w:900,h:750},
  hikarie: {q:'time=day&pose=470,-120,195,285,-45,90,65',w:900,h:750},
  parco: {q:'time=day&pose=-40,150,150,-155,270,50,65',w:900,h:750},
  streamtower: {q:'time=day&pose=55,-145,210,245,-250,100,65',w:900,h:750},
  sakura: {q:'time=day&pose=-75,-160,210,135,-320,95,65',w:900,h:750},

  tactile_entrance_nw: {q:'time=day&pose=-18,9,2.2,-37,14,1.2,60',w:1000,h:750},

  tactile_entrance_east: {q:'time=day&pose=22,-4,2.2,34,3,1,65',w:1000,h:750},
  tactile_entrance_west: {q:'time=day&pose=-20,-15,2.2,-31,-16,.4,65',w:1000,h:750},
  tactile_entrance_north: {q:'time=day&pose=-9,17,2,-8,21,.7,60',w:900,h:675},
  surround_back: {q:'time=day&pose=13,-55,2.2,11.5,-50,1,55',w:900,h:675},

  plaza_facilities: {q:'time=day&pose=6,-40,2,18,-53,2,65',w:1000,h:750},
  plaza_facilities_night: {q:'time=night&pose=6,-40,2,18,-53,2,65',w:1000,h:750},
  plaza_service: {q:'time=day&pose=8,-56,2,11,-62,1.5,60',w:900,h:675},
  plaza_kiosk: {q:'time=day&pose=18,-30,3,34,-46,2.2,60',w:900,h:675},

  terrain: {q:'time=day&pose=0,-180,100,100,-160,0,65',w:1000,h:750},
  station_southeast: {q:'time=day&pose=25,-200,34,85,-135,10,62',w:1000,h:750},

  square: { q:'time=day&pose=8,-52,20,157,-119,110,62',w:900,h:900 },
  fukuras: { q:'time=day&pose=35,-95,16,-29,-200,55,60',w:900,h:900 },
  center244: { q:'time=day&pose=-38,33,4,-68,78,18,50',w:900,h:675 },

  paving_close: { q: 'time=day&pose=8.5,-45,2.2,11.568,-48.686,.7,55', w: 900, h: 675 },
  memorial_front: { q: 'time=day&pose=6.4,-47.7,1.45,9.295,-51.803,.9,48', w: 1000, h: 750 },
  memorial_oblique: { q: 'time=day&pose=5,-49,1.7,9.009,-52.004,.8,52', w: 1000, h: 750 },
  memorial_feet: { q: 'time=day&pose=7.5,-49.1,.8,9.295,-51.803,.32,52', w: 1000, h: 750 },
  surround: { q: 'time=day&pose=6.41,-41.32,2.3,12,-49.3,1,52', w: 1000, h: 750 },
  surround_night: { q: 'time=night&pose=6.41,-41.32,2.3,12,-49.3,1,52', w: 1000, h: 750 },
  statue_front: { q: 'time=day&pose=9.274,-45.409,1.9,11.568,-48.686,1.4,44', w: 750, h: 900 },
  statue_side: { q: 'time=day&pose=7,-52,2.2,11.568,-48.686,1.4,44', w: 900, h: 750 },
  rear_tree_whole: { q: 'time=day&pose=3,-54,5.3,8,-46,4,55', w: 1100, h: 750 },
  rear_tree_front: { q: 'time=day&pose=4,-52,1.8,7.4,-45.5,3.3,55', w: 900, h: 750 },
  rear_tree_oblique: { q: 'time=day&pose=12,-51,2.4,7.4,-45.5,3.4,55', w: 900, h: 750 },
  rear_tree_feet: { q: 'time=day&pose=6,-48,1.4,7.4,-45.5,.35,52', w: 900, h: 750 },
  statue_plaza: { q: 'time=day&pose=16,-35,2,11.568,-48.686,1.3,60', w: 900, h: 675 },
  cover: { q: 'time=day&pose=-7,-4,1.8,-6.272,-2.426,.23,45', w: 900, h: 675 },
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
const browser = await chromium.launch({ args: process.env.CAPTURE_GPU === '1'
  ? ['--ignore-gpu-blocklist']
  : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  let reusablePage;
  let reusableErrors;
  let previousKey;
  for (const [name, v] of Object.entries(views)) {
    if (process.env.VIEWS && !process.env.VIEWS.split(',').includes(name)) continue;
    if (!process.env.FORCE && existsSync(`${out}/${name}.png`)) continue;
    const key = reuseKey(v.q, process.env.EXTRA);
    if (reusablePage && (!key || key !== previousKey)) {
      await reusablePage.close(); reusablePage = undefined; reusableErrors = undefined;
    }
    const reused = !!reusablePage;
    const page = reusablePage ?? await browser.newPage({ viewport: { width: v.w, height: v.h } }); const errors = reusableErrors ?? [];
    if (!reused) {
    await page.route('**/favicon.ico', (r) => r.fulfill({ status: 204 }));
    // QA baseline: old full building list via EXTRA, and the preserved PR82 shell.
    if(process.env.ST2_BASELINE==='1')await page.route('**/buildings/station-north/station-north.glb',r=>r.fulfill({body:readFileSync('assets/buildings/station-north/source/st-2/station-north-pr82.glb'),contentType:'model/gltf-binary'}));
    // QA-only equivalent of approved main: same byte-identical BOX-1, without added layers.
    if(process.env.BOX_BASELINE==='1')await page.route('**/buildings/shibu-hachi-box/viewer.json',async r=>{const response=await r.fetch();const hints=await response.json();delete hints.layers;await r.fulfill({response,body:JSON.stringify(hints),contentType:'application/json'});});
    if(process.env.SURROUND_BASELINE==='1')await page.route('**/street/hachiko-surround/hachiko-surround.glb',r=>r.fulfill({body:execFileSync('git',['show','586dbf5990168bb383d07be83982973536f03263:assets/street/hachiko-surround/web/hachiko-surround.glb'],{maxBuffer:8_000_000}),contentType:'model/gltf-binary'}));
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('response', (r) => { if (r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`); });
    page.on('requestfailed', (r) => errors.push(`${r.url()}: ${r.failure()?.errorText}`));
    await page.goto(`${base}/?capture&${v.q}${process.env.EXTRA ? `&${process.env.EXTRA}` : ""}`);
    await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 300000 });
    }
    if (process.env.REUSE_CAPTURE === '1' && key) {
      reusablePage = page; previousKey = key;
      reusableErrors = errors;
      await page.setViewportSize({width:v.w,height:v.h});
      const query = new URLSearchParams(v.q);
      await page.evaluate(({pose,time}) => window.__viewer.capturePose(pose, time),
        {pose:query.get('pose').split(',').map(Number),time:query.get('time')??'day'});
    }
    await page.waitForTimeout(2500);
    // Freeze the settled QA frame before screenshotting; no application/FPS change.
    await page.evaluate(() => { window.__viewer.freezeFrame(); });
    await page.waitForTimeout(500);
    const state = await page.evaluate(() => ({ boxContents: window.__viewer.boxContents, rearTree: window.__viewer.rearTree, sceneFit: window.__viewer.sceneFit, exterior: window.__viewer.exterior, tactileOuter: window.__viewer.tactileOuter, tactileExtra: window.__viewer.tactileExtra, tactileLinks: window.__viewer.tactileLinks, facilities: window.__viewer.facilities, plaza: window.__viewer.plaza, surround: window.__viewer.surround, hachiko: window.__viewer.hachiko, drainage: window.__viewer.drainage, tactile: window.__viewer.tactile, ground: window.__viewer.ground, street: window.__viewer.street, context: window.__viewer.context, stats: window.__viewer.stats, failed: window.__viewer.failed, status: document.querySelector('#status').textContent }));
    await page.screenshot({ path: `${out}/${name}.png`, timeout: 300000 });
    log[name] = { ...v, extra:process.env.EXTRA??null, boxBaseline:process.env.BOX_BASELINE==='1', state, errors, capturedAt: new Date().toISOString(), cameraPos: await page.evaluate(() => window.__viewer.cameraPos()), camera: await page.evaluate(() => window.__viewer.cameraState()) }; writeFileSync(logPath, JSON.stringify(log, null, 2));
    if (process.env.EXTRA?.includes('reartree=off')) assert.equal(state.rearTree, 'off'); else assert.equal(state.rearTree.ok, true); if (process.env.EXTRA?.includes('fit=off')) assert.equal(state.sceneFit, 'off'); else assert.equal(state.sceneFit.ok, true);
    if (process.env.BASELINE === '1') assert.equal(state.plaza, undefined); else if (process.env.EXTRA?.includes('plaza=off')) assert.equal(state.plaza, 'off'); else assert.equal(state.plaza.ok, true); if (process.env.EXTRA?.includes('surround=off')) assert.equal(state.surround, 'off'); else assert.equal(state.surround.ok, true); if (process.env.EXTRA?.includes('hachiko=off')) assert.equal(state.hachiko, 'off'); else assert.equal(state.hachiko.ok, true); if (process.env.EXTRA?.includes('drainage=off')) assert.equal(state.drainage, 'off'); else assert.equal(state.drainage.ok, true); assert.deepEqual(errors, []); assert.equal(state.status, ''); assert.deepEqual(state.failed, []); assert.equal(state.context.ok, true); assert.equal(state.street.ok, true); if (process.env.EXTRA?.includes('tactile=off')) assert.equal(state.tactile, 'off'); else assert.equal(state.tactile.ok, true); assert.equal(state.ground.ok, true); assert.deepEqual(state.ground.missing, []);
    if (process.env.SUPPLEMENTS === '1') {assert.equal(state.tactileExtra.ok,true);assert.equal(state.tactileLinks.ok,true);}
    if (process.env.EXTERIOR === '1') {assert.equal(state.exterior.ok,true);assert.equal(state.ground.fillReplaced,true);assert.equal(state.exterior.tiles,3);assert.equal(state.tactileOuter.ok,true);assert.equal(state.tactileOuter.attached,true);}
    if (process.env.FACILITIES === '1') assert.equal(state.facilities.ok,true);
    for (const asset of Object.values(state.stats)) assert.deepEqual(asset.layerErrors, []);
    console.log(name, errors.length ? errors : 'ok'); if (!reusablePage) await page.close();
  }
} finally { await browser.close(); }
