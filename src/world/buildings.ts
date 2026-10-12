import { Box3, BoxGeometry, Group, Mesh, MeshBasicMaterial, Object3D, Vector3 } from 'three';
import type { Material, MeshStandardMaterial } from 'three';
import type { PlanXY } from './coords';

export interface ViewerHints {
  arcMid: PlanXY;
  arcNormal: PlanXY;
  arcEnds: [PlanXY, PlanXY];
  floodlights: { arcStart_m: [number, number]; arcEnd_m: [number, number] };
  planBounds: [number, number, number, number];
  crownTop_m: number;
  cameraQ032: { D: number; lat: number; yaw: number; fpx: number; cx: number; cy: number; W: number; H: number; height_m: number };
  sun: { azimuth_deg: number; elevation_deg: number };
}

export type EmissiveTable = Record<string, { kind: string; emit: number[]; estr: number }>;

export interface LoadedBuilding {
  id: string;
  ok: true;
  root: Group;
  hints: ViewerHints;
  emissive: { day: EmissiveTable; night: EmissiveTable };
  stats: { meshes: number; triangles: number; materials: number };
}

export interface FailedBuilding {
  id: string;
  ok: false;
  root: Group;       // placeholder so the rest of the scene still draws
  error: string;
}

export type BuildingResult = LoadedBuilding | FailedBuilding;

/** Everything I/O-bound is injected so the isolation logic can be tested without a browser. */
export interface BuildingIO {
  loadGlb(url: string): Promise<Object3D>;
  loadJson<T>(url: string): Promise<T>;
}

/** Problems that would make a building silently vanish or explode: no geometry, NaN positions, absurd scale. */
export function validateBuilding(root: Object3D): string[] {
  const problems: string[] = [];
  let meshes = 0, triangles = 0;
  root.traverse((o) => {
    const mesh = o as Mesh;
    if (!mesh.isMesh) return;
    meshes++;
    const pos = mesh.geometry.getAttribute('position');
    if (!pos || pos.count === 0) { problems.push(`${mesh.name}: empty mesh`); return; }
    const arr = pos.array as ArrayLike<number>;
    for (let i = 0; i < arr.length; i++) if (!Number.isFinite(arr[i])) { problems.push(`${mesh.name}: non-finite vertex`); break; }
    triangles += mesh.geometry.index ? mesh.geometry.index.count / 3 : pos.count / 3;
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    if (mats.some((m) => !m)) problems.push(`${mesh.name}: missing material`);
  });
  if (meshes === 0) problems.push('no meshes');
  if (triangles === 0) problems.push('no triangles');
  const size = new Box3().setFromObject(root).getSize(new Vector3());
  if (!(size.length() > 1 && size.length() < 5000)) problems.push(`implausible size ${size.toArray().map((v) => v.toFixed(1)).join('x')} m`);
  return problems;
}

function countStats(root: Object3D) {
  let meshes = 0, triangles = 0; const mats = new Set<Material>();
  root.traverse((o) => {
    const mesh = o as Mesh;
    if (!mesh.isMesh) return;
    meshes++;
    const pos = mesh.geometry.getAttribute('position');
    triangles += mesh.geometry.index ? mesh.geometry.index.count / 3 : pos.count / 3;
    (Array.isArray(mesh.material) ? mesh.material : [mesh.material]).forEach((m) => mats.add(m));
  });
  return { meshes, triangles: Math.round(triangles), materials: mats.size };
}

function placeholder(id: string): Group {
  const g = new Group();
  g.name = `${id}:placeholder`;
  const box = new Mesh(new BoxGeometry(20, 40, 20), new MeshBasicMaterial({ color: 0xff3355, wireframe: true }));
  box.position.y = 20;
  g.add(box);
  return g;
}

/**
 * Loads one building. Never throws: a failure returns a wireframe placeholder and the error text, so one broken asset
 * cannot take the other buildings (or the app) down with it.
 */
export async function loadBuilding(id: string, io: BuildingIO, base = '/buildings'): Promise<BuildingResult> {
  try {
    const [root, hints, day, night] = await Promise.all([
      io.loadGlb(`${base}/${id}/${id}.glb`),
      io.loadJson<ViewerHints>(`${base}/${id}/viewer.json`),
      io.loadJson<EmissiveTable>(`${base}/${id}/emissive_day.json`),
      io.loadJson<EmissiveTable>(`${base}/${id}/emissive_night.json`),
    ]);
    const problems = validateBuilding(root);
    if (problems.length) throw new Error(`asset check failed: ${problems.slice(0, 4).join('; ')}`);
    const group = new Group();
    group.name = id;
    group.add(root);
    return { id, ok: true, root: group, hints, emissive: { day, night }, stats: countStats(root) };
  } catch (e) {
    return { id, ok: false, root: placeholder(id), error: e instanceof Error ? e.message : String(e) };
  }
}

/** Day/night switch for baked-in emissive materials: intensities come from the two Cycles builds of the same model. */
export function applyEmissive(root: Object3D, table: EmissiveTable) {
  root.traverse((o) => {
    const mesh = o as Mesh;
    if (!mesh.isMesh) return;
    for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
      const std = m as MeshStandardMaterial;
      const row = table[std.name];
      if (!row || !('emissiveIntensity' in std)) continue;
      std.emissiveIntensity = row.estr;
      if (row.estr > 0 && !std.emissiveMap) std.emissive.setRGB(row.emit[0], row.emit[1], row.emit[2]);
    }
  });
}
