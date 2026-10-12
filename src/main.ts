import { ACESFilmicToneMapping, AgXToneMapping, CircleGeometry, Mesh, MeshStandardMaterial, PCFSoftShadowMap, PerspectiveCamera, Scene, SRGBColorSpace, WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { applyEmissive, loadBuilding, type BuildingIO, type LoadedBuilding } from './world/buildings';
import { Lighting, type TimeOfDay } from './world/lighting';
import { planToWorld } from './world/coords';
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

// a neutral ground disc so the building does not float; streets come in a later gate
const ground = new Mesh(new CircleGeometry(400, 64), new MeshStandardMaterial({ color: 0x5b5a57, roughness: 0.9 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; ground.name = 'ground';
scene.add(ground);

const gltf = new GLTFLoader();
const io: BuildingIO = {
  loadGlb: (url) => gltf.loadAsync(url).then((g) => g.scene),
  loadJson: async (url) => { const r = await fetch(url); if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); },
};

let building: LoadedBuilding | undefined;
let mode: TimeOfDay = params.get('time') === 'night' ? 'night' : 'day';

function setTime(t: TimeOfDay) {
  mode = t;
  $('btn-day').classList.toggle('on', t === 'day'); $('btn-night').classList.toggle('on', t === 'night');
  if (!building) return;
  applyEmissive(building.root, building.emissive[t]);
  lighting.apply(t, building.root);
  bloom.enabled = bloomWanted && quality.bloom && t === 'night';
}

async function start() {
  status('QFRONT を読み込み中…');
  const [envState, result] = await Promise.all([lighting.loadEnvironments(), loadBuilding('qfront', io)]);
  scene.add(result.root);
  if (!result.ok) { status(`QFRONT の読み込みに失敗: ${result.error}（仮の箱を表示）`); return; }
  building = result;
  ground.position.copy(planToWorld(result.hints.arcMid)).setY(0);
  lighting.placeSun(result.hints);
  lighting.placeFloods(result.hints);
  controls.setObstacles([result.root]);
  controls.frameBuilding(result.hints);
  setTime(mode);
  const envNote = envState.day === 'fulfilled' && envState.night === 'fulfilled' ? '' : '（環境マップの一部を読み込めず、反射は簡易表示）';
  status(envNote);
  const view = params.get('view');
  if (view === 'q032') controls.q032View(result.hints);
  else if (view === 'walk') setControl('walk');
  (window as unknown as Record<string, unknown>).__viewer = { ready: true, stats: result.stats };
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
  if (controls.hasProjectionOverride() && building) controls.q032View(building.hints); else camera.updateProjectionMatrix();
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
