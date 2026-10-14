import { Group, InstancedMesh, LOD, Matrix4, Mesh, Quaternion, Vector3, type Object3D } from 'three';

/**
 * Imported street props (assets/street/props): models normalised by tools/props/import_prop.py and placed by
 * layout.json. Each prop GLB is drawn once per part as an InstancedMesh (one draw per part however many copies),
 * with an optional distant LOD ('<id>_lod1') beyond lodDistance. Heights come from the walking surfaces at load,
 * so placements carry only plan x/y and a yaw.
 */
export interface PropPlacement { prop: string; xy: [number, number]; yaw_deg?: number; basis: string }
export interface PropLayout { props: Record<string, { file: string; lodDistance?: number }>; placements: PropPlacement[] }
export interface PropsResult { ok: boolean; root: Group; error?: string; stats: { placed: number; skipped: number; draws: number } }

export async function loadProps(loadGlb: (url: string) => Promise<Object3D>, loadJson: <T>(url: string) => Promise<T>,
  groundAt: (x: number, z: number) => number | null, base = '/street/props'): Promise<PropsResult> {
  const root = new Group(); root.name = 'street:props';
  try {
    const layout = await loadJson<PropLayout>(`${base}/layout.json`);
    let placed = 0, skipped = 0, draws = 0;
    for (const [id, def] of Object.entries(layout.props)) {
      const items = layout.placements.filter((p) => p.prop === id);
      if (!items.length) continue;
      const scene = await loadGlb(`${base}/${def.file}`);
      scene.updateMatrixWorld(true);
      const mats: Matrix4[] = [];
      for (const it of items) {
        const x = it.xy[0], z = -it.xy[1]; const y = groundAt(x, z);
        if (y === null) { skipped++; continue; }                                // never place a prop in mid-air
        mats.push(new Matrix4().compose(new Vector3(x, y, z), new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), ((it.yaw_deg ?? 0) * Math.PI) / 180), new Vector3(1, 1, 1)));
      }
      if (!mats.length) continue;
      const build = (node: Object3D) => {
        const g = new Group();
        node.traverse((o) => {
          const m = o as Mesh; if (!m.isMesh) return;
          const inst = new InstancedMesh(m.geometry, m.material, mats.length); inst.name = `${id}:${m.name}`;
          mats.forEach((mat, i) => inst.setMatrixAt(i, mat.clone().multiply(m.matrixWorld)));
          inst.castShadow = inst.receiveShadow = true; inst.computeBoundingSphere(); g.add(inst); draws++;
        });
        return g;
      };
      const lod1 = scene.getObjectByName(`${id}_lod1`);
      if (lod1) {
        lod1.parent?.remove(lod1);
        // instanced LOD switches per prop type on distance to the group centre (props of one type are spread out,
        // so a generous distance is used); good enough until real props are measured on the owner's PC
        const l = new LOD(); l.addLevel(build(scene), 0); l.addLevel(build(lod1), def.lodDistance ?? 120); l.name = `lod:${id}`; root.add(l);
      } else root.add(build(scene));
      placed += mats.length;
    }
    return { ok: true, root, stats: { placed, skipped, draws } };
  } catch (e) {
    root.clear();
    return { ok: false, root, error: e instanceof Error ? e.message : String(e), stats: { placed: 0, skipped: 0, draws: 0 } };
  }
}
