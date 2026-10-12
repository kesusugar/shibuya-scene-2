import { Group, Mesh, MeshStandardMaterial, SpotLight } from 'three';
import { validateBuilding, type BuildingIO, type CameraFit } from './buildings';

export interface ProjectedMetadata {
  status: 'experimental_only';
  camera: CameraFit;
  camera_status: string;
  light_points: { id: string; position: [number, number, number]; intensity_cd: number; status: 'provisional' }[];
}
export interface ProjectedStreet {
  ok: boolean;
  root: Group;
  error?: string;
  metadata?: ProjectedMetadata;
  lights: SpotLight[];
  setTime(time: 'day' | 'night', enabled?: boolean): void;
}

/** Photo-derived positions are opt-in experiments until the camera is independently validated. */
export async function loadProjectedStreet(io: BuildingIO, url = '/street/core/street_projected.glb'): Promise<ProjectedStreet> {
  const root = new Group(); root.name = 'street:experimental';
  try {
    const [asset, metadata] = await Promise.all([io.loadGlb(url), io.loadJson<ProjectedMetadata>('/street/core/projected.json')]);
    const problems = validateBuilding(asset);
    if (problems.length) throw new Error(problems.join('; '));
    for (const name of ['street_provisional_pole', 'street_lamp_glass', 'street_signal_body', 'street_signal_green', 'street_sign_blue', 'street_sign_red']) {
      if (!asset.getObjectByName(name)) throw new Error(`missing experimental part: ${name}`);
    }
    const c = metadata.camera;
    if (!c || c.pos.length !== 3 || ![...c.pos, c.yaw, c.pitch, c.roll, c.fpx, c.W, c.H].every(Number.isFinite)
      || c.fpx <= 0 || c.W <= 0 || c.H <= 0) throw new Error('invalid reference camera');
    if (metadata.status !== 'experimental_only' || metadata.light_points.length !== 3) throw new Error('invalid experimental metadata');
    for (const p of metadata.light_points) {
      if (p.status !== 'provisional' || p.position.length !== 3 || !p.position.every(Number.isFinite)
        || Math.abs(p.position[0]) > 55 || Math.abs(p.position[2]) > 55 || p.position[1] < 1 || p.position[1] > 15
        || !Number.isFinite(p.intensity_cd) || p.intensity_cd < 0 || p.intensity_cd > 10000) throw new Error('invalid lamp placement');
    }
    root.add(asset);
    const lights = metadata.light_points.map((p) => {
      const light = new SpotLight(0xffe6bf, 0, 40, Math.PI / 3, 0.6, 2);
      light.name = p.id; light.position.fromArray(p.position);
      light.target.position.set(p.position[0], -0.6, p.position[2]);
      light.castShadow = false; root.add(light, light.target); return light;
    });
    const setTime = (time: 'day' | 'night', enabled = true) => {
      lights.forEach((l, i) => { l.intensity = time === 'night' && enabled ? metadata.light_points[i].intensity_cd : 0; });
      asset.traverse((o) => {
        const m = o as Mesh; if (!m.isMesh) return;
        for (const material of Array.isArray(m.material) ? m.material : [m.material]) {
          if (!(material instanceof MeshStandardMaterial)) continue;
          if (material.name === 'street_lamp_glass') {
            material.emissive.setHex(0xffe6bf); material.emissiveIntensity = time === 'night' && enabled ? 8 : 0;
          } else if (material.name === 'street_signal_green') {
            material.emissive.setHex(0x20ff50); material.emissiveIntensity = 2;
          }
        }
      });
    };
    setTime('day');
    return { ok: true, root, lights, metadata, setTime };
  } catch (e) {
    root.clear();
    return { ok: false, root, lights: [], error: e instanceof Error ? e.message : String(e), setTime() {} };
  }
}
