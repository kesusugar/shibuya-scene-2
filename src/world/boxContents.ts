import { Group, Mesh, type Object3D } from 'three';
import { validateBuilding, type BuildingIO } from './buildings';

export interface BoxLayout {
  origin: [number, number, number]; yaw: number;
  parts: { id: string; file: string; position: [number, number, number]; yaw: number; scale: number }[];
}
export interface BoxContentsResult {
  ok: boolean; root: Group; error?: string;
  stats: { meshes: number; triangles: number; parts: string[] };
}
/** A single architecture parent; source GLBs are already Y-up. Positions are
 * recorded in the architecture's Blender local metres, not a second world fit. */
export async function loadBoxContents(io: BuildingIO): Promise<BoxContentsResult> {
  const root = new Group(); root.name = 'street:box-contents';
  const stats = { meshes: 0, triangles: 0, parts: [] as string[] };
  try {
    const layout = await io.loadJson('/street/box-contents/layout.json') as BoxLayout;
    if (![...layout.origin, layout.yaw].every(v => typeof v === 'number' && Number.isFinite(v))) throw Error('Invalid BOX parent');
    root.position.set(layout.origin[0], layout.origin[2], -layout.origin[1]);
    root.rotation.y = layout.yaw * Math.PI / 180;
    if (new Set(layout.parts.map(p => p.id)).size !== layout.parts.length) throw Error('Duplicate BOX part');
    for (const p of layout.parts) {
      if (![...p.position, p.yaw, p.scale].every(v => typeof v === 'number' && Number.isFinite(v)) || p.scale <= 0) throw Error(`Invalid transform: ${p.id}`);
      const model: Object3D = await io.loadGlb(`/street/box-contents/${p.file}`);
      const errors = validateBuilding(model, 0.01); if (errors.length) throw Error(`${p.id}: ${errors.join(', ')}`);
      const mount = new Group(); mount.name = `contents:${p.id}`;
      mount.position.set(p.position[0], p.position[2], -p.position[1]);
      mount.rotation.y = p.yaw * Math.PI / 180; mount.scale.setScalar(p.scale); mount.add(model);
      model.traverse(o => { const m = o as Mesh; if (!m.isMesh) return;
        stats.meshes++; stats.triangles += (m.geometry.index?.count ?? m.geometry.getAttribute('position').count) / 3;
        m.receiveShadow = true; m.castShadow = true;
        // Furniture remains non-emissive; no invented screen contents or bloom.
        for (const material of Array.isArray(m.material) ? m.material : [m.material]) material.name = `street_box_contents_${material.name}`;
      });
      root.add(mount); stats.parts.push(p.id);
    }
    return {ok:true, root, stats};
  } catch (error) {
    root.clear(); return {ok:false, root, error:String(error), stats:{meshes:0,triangles:0,parts:[]}};
  }
}
