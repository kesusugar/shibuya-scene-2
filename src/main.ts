import { ACESFilmicToneMapping, AgXToneMapping, CircleGeometry, Mesh, MeshStandardMaterial, PCFSoftShadowMap, PerspectiveCamera, Scene, SRGBColorSpace, WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { applyEmissive, hasArc, loadBuilding, type BuildingIO, type BuildingResult, type LoadedBuilding } from './world/buildings';
import { Lighting, type TimeOfDay } from './world/lighting';
import { ViewerControls } from './controls/viewer-controls';
import { FrameStats } from './perf/frame-stats';
import { pickQuality } from './core/quality';
import { runBenchmark } from './perf/benchmark';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { Vector2 } from 'three';

const params = new URLSearchParams(location.search);
const $ = (id: string) => document.getElementById(id)!;
const status = (msg: string) => { $('status').textContent = msg; };
if (params.has('capture')) $('hud').style.visibility = 'hidden';   // clean stills; the numbers stay readable via #perf

const quality = pickQuality(params.get('q'));
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

// a neutral ground disc so the buildings do not float; streets come in a later gate
const ground = new Mesh(new CircleGeometry(400, 64), new MeshStandardMaterial({ color: 0x5b5a57, roughness: 0.9 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; ground.name = 'ground';
scene.add(ground);

const gltf = new GLTFLoader();
const io: BuildingIO = {
  loadGlb: (url) => gltf.loadAsync(url).then((g) => g.scene),
  loadJson: async (url) => { const r = await fetch(url); if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); },
};

// Buildings load side by side and independently: one broken asset shows a red placeholder, the rest still draw.
const ids = (params.get('buildings') ?? 'qfront,magnet,eiraku').split(',').map((s) => s.trim()).filter(Boolean);
const NAMES: Record<string, string> = { qfront: 'QFRONT', magnet: 'MAGNET', eiraku: '栄楽ビル' };
let loaded: LoadedBuilding[] = [];
let building: LoadedBuilding | undefined;   // the building the camera presets frame (QFRONT when present)
let mode: TimeOfDay = params.get('time') === 'night' ? 'night' : 'day';

function setTime(t: TimeOfDay) {
  mode = t;
  $('btn-day').classList.toggle('on', t === 'day'); $('btn-night').classList.toggle('on', t === 'night');
  if (!building) return;
  for (const b of loaded) applyEmissive(b.root, b.emissive[t]);
  lighting.apply(t, loaded.map((b) => b.root));
  bloom.enabled = bloomWanted && quality.bloom && t === 'night';
}

async function start() {
  status(`${ids.map((id) => NAMES[id] ?? id).join('・')} を読み込み中…`);
  const [envState, results] = await Promise.all([lighting.loadEnvironments(), Promise.all(ids.map((id) => loadBuilding(id, io)))]);
  results.forEach((r: BuildingResult) => scene.add(r.root));
  loaded = results.filter((r): r is LoadedBuilding => r.ok);
  const problems = [
    ...results.filter((r) => !r.ok).map((r) => `${NAMES[r.id] ?? r.id} の読み込みに失敗: ${'error' in r ? r.error : ''}（仮の箱を表示）`),
    ...loaded.flatMap((b) => b.layerErrors.map((e) => `${NAMES[b.id] ?? b.id} の看板レイヤーを読み込めず: ${e}`)),
  ];
  building = loaded.find((b) => b.id === 'qfront') ?? loaded[0];
  if (!building) { status(problems.join('\n')); return; }
  lighting.placeSun(building.hints);
  for (const b of loaded) lighting.placeFloods(b.hints);
  controls.setObstacles(loaded.map((b) => b.root));
  controls.frameBuilding(building.hints);
  setTime(mode);
  const envNote = envState.day === 'fulfilled' && envState.night === 'fulfilled' ? '' : '（環境マップの一部を読み込めず、反射は簡易表示）';
  status([...problems, envNote].filter(Boolean).join('\n'));
  const fit = loaded.find((b) => b.hints.cameraFit);
  ($('btn-m027') as HTMLButtonElement).disabled = !fit;
  const view = params.get('view');
  if (view === 'q032') controls.q032View(building.hints);
  else if (view === 'm027' && fit?.hints.cameraFit) controls.fitView(fit.hints.cameraFit, building.hints);
  else if (view === 'walk') setControl('walk');
  (window as unknown as Record<string, unknown>).__viewer = {
    ready: true,
    stats: Object.fromEntries(loaded.map((b) => [b.id, { ...b.stats, layers: b.layers, layerErrors: b.layerErrors }])),
    failed: results.filter((r) => !r.ok).map((r) => r.id),
  };
}

function setControl(m: 'orbit' | 'walk') {
  if (!building) return;
  controls.setMode(m, building.hints);
  $('btn-orbit').classList.toggle('on', m === 'orbit'); $('btn-walk').classList.toggle('on', m === 'walk');
}

$('btn-day').onclick = () => setTime('day');
$('btn-night').onclick = () => setTime('night');
$('btn-orbit').onclick = () => setControl('orbit');
$('btn-walk').onclick = () => setControl('walk');
$('btn-q032').onclick = () => building && controls.q032View(building.hints);
$('btn-m027').onclick = () => {
  const fit = loaded.find((b) => b.hints.cameraFit);
  if (fit?.hints.cameraFit && building) controls.fitView(fit.hints.cameraFit, building.hints);
};
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

start().catch((e) => status(`起動エラー: ${e instanceof Error ? e.message : e}`));
