import { ACESFilmicToneMapping, AgXToneMapping, CircleGeometry, Mesh, MeshStandardMaterial, PCFSoftShadowMap, PerspectiveCamera, Scene, SRGBColorSpace, WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { applyEmissive, groundOffset, hasArc, loadBuilding, type BuildingIO, type BuildingResult, type LoadedBuilding } from './world/buildings';
import { loadGround, type GroundResult } from './world/ground';
import { loadProjectedStreet, type ProjectedStreet, type ProjectedMetadata } from './world/projected-street';
import { loadStreet, type StreetResult } from './world/street';
import { loadContext, type ContextResult } from './world/context';
import { applyClassPass, applyLook, parseLook } from './world/look';
import { Color } from 'three';
import { Lighting, type TimeOfDay } from './world/lighting';
import { ViewerControls } from './controls/viewer-controls';
import { FrameStats } from './perf/frame-stats';
import { pickQuality } from './core/quality';
import { runBenchmark } from './perf/benchmark';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { Vector2, Vector3 } from 'three';

const params = new URLSearchParams(location.search);
const $ = (id: string) => document.getElementById(id)!;
const status = (msg: string) => { $('status').textContent = msg; };
if (params.has('capture')) $('hud').style.visibility = 'hidden';   // clean stills; the numbers stay readable via #perf

const quality = pickQuality(params.get('q'));
const look = parseLook(params.get('look'));
const renderer = new WebGLRenderer({ antialias: quality.antialias, powerPreference: 'high-performance', preserveDrawingBuffer: params.has('capture') });
renderer.setPixelRatio(Math.min(devicePixelRatio, Number(params.get('dpr') ?? quality.maxDpr)));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = SRGBColorSpace;
renderer.toneMapping = params.get('tone') === 'aces' ? ACESFilmicToneMapping : AgXToneMapping;   // AgX: same as the Cycles renders
renderer.shadowMap.enabled = quality.shadows;
renderer.shadowMap.type = PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new Scene();
const camera = new PerspectiveCamera(55, innerWidth / innerHeight, 0.3, 3000);
const lighting = new Lighting(renderer, scene, quality.shadowMapSize);
if (params.has('flood')) lighting.floodIntensity = Number(params.get('flood'));
const controls = new ViewerControls(camera, renderer.domElement);
const stats = new FrameStats();

// bloom only at night (lit letters, LED screen, shop windows), and only from the medium preset up
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
// the composer works on linear radiance before tone mapping: only the lit letters, LED and lamps (>~8) should bloom
// Off by default: under headless SwiftShader the pass hazes the whole frame (cause not isolated yet). ?bloom=on to try on a real GPU.
const bloomWanted = params.get('bloom') === 'on';
const bloom = new UnrealBloomPass(new Vector2(innerWidth, innerHeight), Number(params.get('bs') ?? 0.35), 0.35, Number(params.get('bt') ?? 3));
composer.addPass(bloom);
composer.addPass(new OutputPass());

// a neutral disc beyond the Core ground (and the only ground if the Core ground fails or ?ground=off); it sits just
// under the lowest Core road surface (T.P. 14.4 = -0.6 m in the common datum)
const useGround = params.get('ground') !== 'off';
const ground = new Mesh(new CircleGeometry(1500, 96), new MeshStandardMaterial({ color: 0x5b5a57, roughness: 0.9 }));
ground.rotation.x = -Math.PI / 2; ground.position.y = useGround ? -0.62 : 0; ground.receiveShadow = true; ground.name = 'ground';
scene.add(ground);
let coreGround: GroundResult | undefined;
let coreStreet: StreetResult | undefined;
let coreContext: ContextResult | undefined;
let projectedStreet: ProjectedStreet | undefined;

const gltf = new GLTFLoader();
const io: BuildingIO = {
  loadGlb: (url) => gltf.loadAsync(url).then((g) => g.scene),
  loadJson: async (url) => { const r = await fetch(url); if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); },
};

// Buildings load side by side and independently: one broken asset shows a red placeholder, the rest still draw.
const ids = (params.get('buildings') ?? 'qfront,magnet,eiraku,west-block,ekimae,station-concourse,station-north,station-service,station-west-viaduct').split(',').map((s) => s.trim()).filter(Boolean).filter((id) => params.get('context') !== 'nostation' || !['station-concourse', 'station-north', 'station-service', 'station-west-viaduct'].includes(id));
const NAMES: Record<string, string> = { qfront: 'QFRONT', magnet: 'MAGNET', eiraku: '栄楽ビル', 'west-block': 'センター街入口西側街区', ekimae: '渋谷駅前ビル', 'station-concourse': '駅・マークシティ連絡通路', 'station-north': 'JR北側ホーム上屋', 'station-service': '駅西側の小施設', 'station-west-viaduct': '駅西側の高架部（推定）' };
let loaded: LoadedBuilding[] = [];
let building: LoadedBuilding | undefined;   // the building the camera presets frame (QFRONT when present)
let mode: TimeOfDay = params.get('time') === 'night' ? 'night' : 'day';

function setTime(t: TimeOfDay) {
  mode = t;
  $('btn-day').classList.toggle('on', t === 'day'); $('btn-night').classList.toggle('on', t === 'night');
  if (!building) return;
  lighting.apply(t, loaded.map((b) => b.root));
  const env = { map: scene.environment, intensity: scene.environmentIntensity };
  for (const b of loaded) { applyEmissive(b.root, b.emissive[t]); applyLook(b.root, t, look, b.emissive.day, env); }
  const groundLook = projectedStreet?.ok && params.get('lamps') !== 'off' && !params.get('look')?.includes('nightGround:') ? { ...look, nightGround: 0 } : look;
  if (coreGround?.ok) applyLook(coreGround.root, t, groundLook);
  projectedStreet?.setTime(t, params.get('lamps') !== 'off');
  if (coreStreet?.ok) { applyLook(coreStreet.root, t, look, undefined, env); coreStreet.setTime(t); }
  coreContext?.setTime(t);
  renderer.toneMappingExposure = t === 'day' ? look.dayExposure : look.nightExposure;
  bloom.enabled = bloomWanted && quality.bloom && t === 'night';
}

async function start() {
  status(`${ids.map((id) => NAMES[id] ?? id).join('・')} を読み込み中…`);
  const [envState, results, groundRes, streetRes, projectedRes, contextRes] = await Promise.all([lighting.loadEnvironments(), Promise.all(ids.map((id) => loadBuilding(id, io))),
    useGround ? loadGround(io.loadGlb, params.get('groundurl') === 'missing' ? '/ground/core/missing.glb' : undefined) : Promise.resolve(undefined),
    params.get('street') !== 'off' ? loadStreet(io.loadGlb, params.get('streeturl') === 'missing' ? '/street/core/missing.glb' : undefined, params.get('street') !== 'entrances') : Promise.resolve(undefined),
    params.get('street') === 'projected' ? loadProjectedStreet(io, params.get('projectedurl') === 'missing' ? '/street/core/missing.glb' : undefined) : Promise.resolve(undefined),
    params.get('context') !== 'off' ? loadContext(io.loadGlb, params.get('contexturl') === 'missing' ? '/context/core/missing.glb' : undefined, params.get('context') !== 'nostation') : Promise.resolve(undefined)]);
  results.forEach((r: BuildingResult) => scene.add(r.root));
  coreGround = groundRes;
  coreStreet = streetRes;
  coreContext = contextRes;
  if (coreContext?.ok) scene.add(coreContext.root);
  projectedStreet = projectedRes;
  if (projectedStreet?.ok) scene.add(projectedStreet.root);
  $('provisional').textContent = projectedStreet?.ok ? '仮配置：支柱の位置・寸法・光量は確認待ち（橙色）' : coreStreet?.ok ? '街路設備は仮：出入口・樹木は2025年OSMの位置、信号・柵は規則による配置、形は標準寸法の汎用品' : '';
  if (coreStreet?.ok) scene.add(coreStreet.root);
  if (coreGround?.ok) { scene.add(coreGround.root); controls.setGround([coreGround.root]); }
  else if (coreGround) ground.position.y = 0;   // no Core ground: the disc goes back to y = 0
  controls.setGround([...(coreGround?.ok ? [coreGround.root] : []), ...(coreStreet?.ok ? coreStreet.walkSurfaces : [])]);
  loaded = results.filter((r): r is LoadedBuilding => r.ok);
  if (loaded.some((b) => b.id === 'west-block')) $('provisional').textContent += '\n西側街区の外観は試作、看板は2025年1月の写真を参照';
  if (loaded.some((b) => b.id === 'ekimae')) $('provisional').textContent += '\n渋谷駅前ビルの外観は試作、看板は2025年11月の写真を参照';
  if (loaded.some((b) => b.id === 'station-concourse')) $('provisional').textContent += '\n駅側の連絡通路は試作、開口・窓・内部・工事用の囲いの寸法と配置、光量は推定';
  if (loaded.some((b) => b.id === 'station-north')) $('provisional').textContent += '\nJR北側ホーム上屋は試作、柱・梁・床の帯の配置は推定、南側は外観未確認';
  if (loaded.some((b) => b.id === 'station-service')) $('provisional').textContent += '\n駅西側の小施設は試作、設備棟との対応・外装・換気口は推定、正面の同定は未完了';
  if (loaded.some((b) => b.id === 'station-west-viaduct')) $('provisional').textContent += '\n駅西側高架は試作、写真との対応・桁・柱・補強・養生網の寸法と配置は推定';
  // QA only: ?datum=off reproduces the scene before the common datum (every model at its own 0 m = Y 0)
  if (params.get('datum') === 'off') for (const b of loaded) { b.hints.groundElevationTP = undefined; b.root.position.y = 0; }
  const problems = [
    ...(projectedStreet && !projectedStreet.ok ? [`写真からの仮配置を読み込めず: ${projectedStreet.error}（通常表示を継続）`] : []),
    ...(coreContext && !coreContext.ok ? [`周辺の建物（C段階）の読み込みに失敗: ${coreContext.error}（他は表示を継続）`] : []),
    ...(coreStreet && !coreStreet.ok ? [`街路設備の読み込みに失敗: ${coreStreet.error}（建物と地面は表示を継続）`] : []),
    ...(coreGround && !coreGround.ok ? [`地面の読み込みに失敗: ${coreGround.error}（灰色の円盤を表示）`] : []),
    ...(coreGround?.ok && coreGround.missing.length ? [`地面の一部がない: ${coreGround.missing.join(', ')}`] : []),
    ...results.filter((r) => !r.ok).map((r) => `${NAMES[r.id] ?? r.id} の読み込みに失敗: ${'error' in r ? r.error : ''}（仮の箱を表示）`),
    ...loaded.flatMap((b) => b.layerErrors.map((e) => `${NAMES[b.id] ?? b.id} の看板レイヤーを読み込めず: ${e}`)),
  ];
  building = loaded.find((b) => b.id === 'qfront') ?? loaded[0];
  if (!building) { status(problems.join('\n')); return; }
  lighting.placeSun(building.hints);
  for (const b of loaded) lighting.placeFloods(b.hints);
  controls.setObstacles([...loaded.map((b) => b.root), ...(coreContext?.ok ? [coreContext.root] : []), ...(coreStreet?.ok ? [coreStreet.root] : []), ...(projectedStreet?.ok ? [projectedStreet.root] : [])]);
  controls.frameBuilding(building.hints);
  setTime(mode);
  const envNote = envState.day === 'fulfilled' && envState.night === 'fulfilled' ? '' : '（環境マップの一部を読み込めず、反射は簡易表示）';
  status([...problems, envNote].filter(Boolean).join('\n'));
  const fit = loaded.find((b) => b.hints.cameraFit);
  ($('btn-m027') as HTMLButtonElement).disabled = !fit;
  const view = params.get('view');
  if (view === 'q032') controls.q032View(building.hints);
  else if (view === 'm027' && fit?.hints.cameraFit) showFit(fit);
  else if (view === 'walk') setControl('walk');
  // QA: ?pass=class paints every surface by material class (look-metrics.py compares it with the photograph)
  if (params.get('pass') === 'class') {
    for (const b of loaded) applyClassPass(b.root, { ...b.emissive.day });
    if (coreGround?.ok) applyClassPass(coreGround.root);
    if (coreStreet?.ok) applyClassPass(coreStreet.root);
    if (coreContext?.ok) applyClassPass(coreContext.root);
    if (projectedStreet?.ok) applyClassPass(projectedStreet.root);
    ground.material = new MeshStandardMaterial({ color: 0x000000 }); ground.visible = false;
    scene.background = new Color(0x000000); scene.environment = null; bloom.enabled = false;
  }
  const pose = params.get('pose');   // QA: pose=x,y,z,tx,ty,tz[,vfov] in plan metres, heights in the common datum
  if (pose) { const v = pose.split(',').map(Number); controls.poseView([v[0], v[1], v[2]], [v[3], v[4], v[5]], v[6] || 55, building.hints); }
  if (params.get('streetref') === 'stream2025') {
    const metadata = projectedStreet?.metadata ?? await io.loadJson<ProjectedMetadata>('/street/core/projected.json');
    controls.fitView(metadata.camera, building.hints, 0);
  }
  (window as unknown as Record<string, unknown>).__viewer = {
    ready: true,
    stats: Object.fromEntries(loaded.map((b) => [b.id, { ...b.stats, layers: b.layers, layerErrors: b.layerErrors }])),
    failed: results.filter((r) => !r.ok).map((r) => r.id),
    ground: coreGround ? { ok: coreGround.ok, error: coreGround.error, missing: coreGround.missing, ...coreGround.stats } : 'off',
    context: coreContext ? { ok: coreContext.ok, error: coreContext.error, ...coreContext.stats } : 'off',
    street: coreStreet ? { ok: coreStreet.ok, error: coreStreet.error, mode: params.get('street') === 'entrances' ? 'entrances' : 'all', ...coreStreet.stats } : 'off',
    projected: projectedStreet ? { ok: projectedStreet.ok, error: projectedStreet.error, status: projectedStreet.metadata?.status, cameraStatus: projectedStreet.metadata?.camera_status, lamps: projectedStreet.lights.map((l) => ({ id: l.name, intensity: l.intensity, position: l.position.toArray() })), groundEmissive: projectedStreet.ok && params.get('lamps') !== 'off' && !params.get('look')?.includes('nightGround:') ? 0 : look.nightGround } : 'off',
    offsets: Object.fromEntries(loaded.map((b) => [b.id, b.root.position.y])),
    // QA: camera position and the Core ground height under it (walk mode keeps the eye 1.6 m above it)
    cameraPos: () => camera.position.toArray(),
    projectPlan: (p: [number, number, number]) => { const v = new Vector3(p[0], p[2], -p[1]).project(camera); return [(v.x * 0.5 + 0.5) * innerWidth, (-v.y * 0.5 + 0.5) * innerHeight]; },
    bench: null as unknown,
    groundUnderCamera: () => controls.groundY(camera.position.x, camera.position.z),
  };
}

function setControl(m: 'orbit' | 'walk') {
  if (!building) return;
  controls.setMode(m, building.hints);
  $('btn-orbit').classList.toggle('on', m === 'orbit'); $('btn-walk').classList.toggle('on', m === 'walk');
}

$('btn-day').onclick = () => setTime('day');
$('btn-night').onclick = () => setTime('night');
$('btn-orbit').onclick = () => { setControl('orbit'); restoreSun(); };
$('btn-walk').onclick = () => { setControl('walk'); restoreSun(); };
$('btn-q032').onclick = () => { if (building) { controls.q032View(building.hints); restoreSun(); } };
$('btn-m027').onclick = () => {
  const fit = loaded.find((b) => b.hints.cameraFit);
  if (fit) showFit(fit);
};

/** The photo-fitted view also takes that photo's sun (M027: 2025-09-01 13:18, az 207 / el 57); other views keep QFRONT's. */
function showFit(fit: LoadedBuilding) {
  if (!fit.hints.cameraFit || !building) return;
  controls.fitView(fit.hints.cameraFit, building.hints, groundOffset(fit.hints));
  lighting.placeSun(fit.hints);
}
function restoreSun() { if (building) lighting.placeSun(building.hints); }
$('btn-bench').onclick = async () => {
  const btn = $('btn-bench') as HTMLButtonElement; btn.disabled = true; btn.textContent = '計測中（30秒）…';
  const r = await runBenchmark(stats, renderer, { quality: quality.name, time: mode, view: controls.mode + (controls.hasProjectionOverride() ? ':q032' : '') });
  $('bench-out').textContent = JSON.stringify(r, null, 1); btn.disabled = false; btn.textContent = '30秒計測';
  console.log('BENCHMARK', JSON.stringify(r));
};

addEventListener('resize', () => {
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  if (controls.hasProjectionOverride() && building && hasArc(building.hints) && !controls.fitActive) controls.q032View(building.hints); else camera.updateProjectionMatrix();
});

let lastHud = 0;
renderer.setAnimationLoop(() => {
  const dt = Math.min(0.1, stats.tick());
  controls.update(dt);
  if (bloom.enabled) composer.render(); else renderer.render(scene, camera);
  const now = performance.now();
  if (now - lastHud > 500) { $('perf').textContent = stats.report(renderer); lastHud = now; }
});

start().then(() => { if (params.get('bench') === 'auto') autoBench(); }).catch((e) => status(`起動エラー: ${e instanceof Error ? e.message : e}`));

/**
 * ?bench=auto: the owner's one-URL measurement. Visits the fixed Core views (day and night), records 10 s each after a
 * 2 s settle, then shows one JSON block to copy back. Same counters as the 30 s button (frame times, draw calls, tris).
 */
const BENCH_VIEWS: [string, TimeOfDay, string][] = [
  ['c01_qfront', 'day', '6.5,-2.0,1.516,-8,29,12,55'], ['c01_qfront', 'night', '6.5,-2.0,1.516,-8,29,12,55'],
  ['c02_hachiko', 'day', '11.6,-47.0,1.871,6,10,6,55'], ['x01_walkway', 'day', '-12.6,-68.2,10.2,0.8,30.7,16.2,52.2'],
  ['top_down', 'day', '6.5,-30,190,6.5,-1.9,0,48'], ['m027', 'day', 'm027'], ['q032', 'night', 'q032'],
];
async function autoBench() {
  if (!building) return;
  const out: unknown[] = [];
  for (const [name, t, pose] of BENCH_VIEWS) {
    status(`自動計測中: ${name}（${t}）… ${out.length + 1}/${BENCH_VIEWS.length}`);
    setTime(t);
    if (pose === 'm027') { const fit = loaded.find((b) => b.hints.cameraFit); if (fit) showFit(fit); }
    else if (pose === 'q032') controls.q032View(building.hints);
    else { const v = pose.split(',').map(Number); controls.poseView([v[0], v[1], v[2]], [v[3], v[4], v[5]], v[6], building.hints); }
    await new Promise((r) => setTimeout(r, 2000));
    out.push({ name, ...(await runBenchmark(stats, renderer, { quality: quality.name, time: t, view: name }, 10)) });
  }
  const text = JSON.stringify({ kind: 'shibuya-core-bench', version: 1, ground: coreGround?.ok ?? false, results: out });
  $('bench-out').textContent = text; console.log('BENCHMARK_AUTO', text);
  (window as unknown as { __viewer: { bench: unknown } }).__viewer.bench = out;
  status('自動計測が終わりました。下の結果（JSON）をすべてコピーして送ってください。');
  navigator.clipboard?.writeText(text).catch(() => undefined);
}
