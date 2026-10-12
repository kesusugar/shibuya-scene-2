import {
  AmbientLight, Color, DirectionalLight, EquirectangularReflectionMapping, Group, HemisphereLight, Object3D,
  PMREMGenerator, Scene, SpotLight, Texture, Vector3, WebGLRenderer, Mesh, MeshStandardMaterial,
} from 'three';
import { HDRLoader } from 'three/examples/jsm/loaders/HDRLoader.js';
import { planToWorld } from './coords';
import type { ViewerHints } from './buildings';

export type TimeOfDay = 'day' | 'night';

interface EnvSet { background: Texture; env: Texture }

/**
 * Day/night lighting rig. Day mirrors the Cycles set-up of QFRONT v5 (sun az 152 deg / el 38 deg, street HDRI for
 * reflections); night uses the dusk HDRI at low strength, a deep-blue sky and the floodlight washes on the side faces.
 */
export class Lighting {
  readonly group = new Group();
  private sun = new DirectionalLight(0xfff2e0, 6.0);
  private hemi = new HemisphereLight(0xb8c8e8, 0x4a4640, 0.6);
  private ambient = new AmbientLight(0xffffff, 0);
  private floods: SpotLight[] = [];
  private sets: Partial<Record<TimeOfDay, EnvSet>> = {};
  mode: TimeOfDay = 'day';
  floodIntensity = 3000;

  constructor(private renderer: WebGLRenderer, private scene: Scene, shadowMapSize = 2048) {
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(shadowMapSize, shadowMapSize);
    const cam = this.sun.shadow.camera;
    cam.left = -60; cam.right = 60; cam.top = 60; cam.bottom = -60; cam.near = 1; cam.far = 400;
    this.sun.shadow.bias = -0.0004; this.sun.shadow.normalBias = 0.03;
    this.group.add(this.sun, this.sun.target, this.hemi, this.ambient);
    scene.add(this.group);
  }

  /** Sun direction from azimuth (clockwise from north) and elevation, aimed at the building. */
  placeSun(hints: ViewerHints) {
    const az = (hints.sun.azimuth_deg * Math.PI) / 180, el = (hints.sun.elevation_deg * Math.PI) / 180;
    const toSun = new Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)); // east, up, south
    const target = planToWorld(hints.arcMid, 20).add(new Vector3(-6, 0, -12));
    this.sun.target.position.copy(target);
    this.sun.position.copy(target).addScaledVector(toSun, 200);
  }

  /** Floodlight washes from the arm tips at the arc ends, down the side faces (as in the Q031 dusk photo). */
  placeFloods(hints: ViewerHints) {
    const mid = planToWorld(hints.arcMid);
    const front = planToWorld(hints.arcNormal).normalize();          // outward normal of the curved front
    const pairs: [typeof hints.arcEnds[number], [number, number]][] = [[hints.arcEnds[0], hints.floodlights.arcStart_m], [hints.arcEnds[1], hints.floodlights.arcEnd_m]];
    for (const [end, [z0, z1]] of pairs) {
      const p = planToWorld(end);
      const out = p.clone().sub(mid).setY(0).normalize();
      for (let k = 0; k < 2; k++) {
        const h = z0 + ((z1 - z0) * k);
        // the arms reach out past the corner and wash back along the side face (Q031), not onto the street
        const s = new SpotLight(0xffe2c0, 0, 55, Math.PI / 7, 0.8, 1.4);
        s.position.copy(p).addScaledVector(out, 3).addScaledVector(front, 2).setY(h);
        s.target.position.copy(p).addScaledVector(front, -14).addScaledVector(out, -1).setY(h - 16);
        this.group.add(s, s.target);
        this.floods.push(s);
      }
    }
  }

  async loadEnvironments(base = '/env') {
    const pmrem = new PMREMGenerator(this.renderer);
    const loader = new HDRLoader();
    const load = async (file: string): Promise<EnvSet> => {
      const tex = await loader.loadAsync(`${base}/${file}`);
      tex.mapping = EquirectangularReflectionMapping;
      return { background: tex, env: pmrem.fromEquirectangular(tex).texture };
    };
    const [day, night] = await Promise.allSettled([load('wide_street_01_1k.hdr'), load('shanghai_bund_1k.hdr')]);
    if (day.status === 'fulfilled') this.sets.day = day.value;
    if (night.status === 'fulfilled') this.sets.night = night.value;
    pmrem.dispose();
    return { day: day.status, night: night.status };
  }

  apply(mode: TimeOfDay, building?: Object3D) {
    this.mode = mode;
    const day = mode === 'day';
    const set = this.sets[mode];
    this.scene.environment = set?.env ?? null;
    this.scene.environmentIntensity = day ? 0.45 : 0.06;
    // the photographed sky is the backdrop; the HDRI street only feeds reflections
    this.scene.background = new Color(day ? 0x3f6fb5 : 0x0b2a78);
    this.sun.intensity = day ? 6.0 : 0;
    this.sun.castShadow = day;
    this.hemi.intensity = day ? 0.6 : 0.08;
    this.hemi.color.set(day ? 0xb8c8e8 : 0x3050a0);
    for (const f of this.floods) f.intensity = day ? 0 : this.floodIntensity;
    this.renderer.toneMappingExposure = day ? 1.0 : 1.35;
    building?.traverse((o) => {
      const mesh = o as Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = mesh.receiveShadow = true;
      for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
        const std = m as MeshStandardMaterial;
        if (std.transparent) { std.depthWrite = false; mesh.castShadow = false; }
      }
    });
  }
}
