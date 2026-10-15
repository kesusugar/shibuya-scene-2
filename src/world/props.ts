import { Box3, Group, InstancedMesh, Matrix4, Mesh, Quaternion, Vector3, type Material, type Object3D } from 'three';

export interface PropPlacement {
  id: string; prop: string; xy: [number, number]; yaw_deg: number;
  basis: string; source_photo: string; observed_date: string; status: 'estimated';
}
export interface PropLayout {
  props: Record<string, { file: string; size_m: [number, number, number] }>;
  placements: PropPlacement[];
}
export interface PropAnchor {
  id: string; prop: string; xy: [number, number]; yaw_deg: number; ground: number; baseGap: number;
  size_m: [number, number, number];
}
export interface PropsResult {
  ok: boolean; root: Group; errors: string[]; anchors: PropAnchor[];
  stats: { placed: number; skipped: number; triangles: number; draws: number };
}
/** Canonical dots GLBs remain unchanged. Same-type instances share geometry and materials.
 * Foot corners and centre must have ground, with <= 6cm variation; never fall back to Y=0.
 * A failed prop leaves the other types visible and is reported to the UI.
 */
export async function loadProps(loadGlb: (url: string) => Promise<Object3D>, loadJson: <T>(url: string) => Promise<T>,
  groundAt: (x: number, z: number) => number | null, base = '/street/props'): Promise<PropsResult> {
  const root = new Group(); root.name = 'street:props';
  const result: PropsResult = { ok: true, root, errors: [], anchors: [], stats: { placed: 0, skipped: 0, triangles: 0, draws: 0 } };
  try {
    const layout = await loadJson<PropLayout>(`${base}/layout.json`);
    const ids = new Set<string>();
    for (const p of layout.placements) {
      if (ids.has(p.id) || !layout.props[p.prop] || ![...p.xy,p.yaw_deg].every(Number.isFinite) || !p.basis || !p.source_photo) throw new Error(`Invalid placement: ${p.id}`);
      ids.add(p.id);
    }
    for (const [id, def] of Object.entries(layout.props)) {
      const items = layout.placements.filter(p => p.prop === id); if (!items.length) continue;
      try {
        const asset = await loadGlb(`${base}/${def.file}`); asset.updateMatrixWorld(true);
        const box = new Box3().setFromObject(asset), size = box.getSize(new Vector3());
        const dims: [number,number,number] = [size.x,size.z,size.y];
        if (!dims.every((v,i)=>Number.isFinite(v) && v>0 && Math.abs(v-def.size_m[i])<.02)) throw new Error('Unexpected dimensions (metres required)');
        const matrices: Matrix4[] = [], anchors: PropAnchor[] = [];
        for (const p of items) {
          const rotation = new Quaternion().setFromAxisAngle(new Vector3(0,1,0),p.yaw_deg*Math.PI/180);
          const heights: number[] = [];
          for (const x of [box.min.x,box.getCenter(new Vector3()).x,box.max.x]) for (const z of [box.min.z,box.getCenter(new Vector3()).z,box.max.z]) {
            const q = new Vector3(x,0,z).applyQuaternion(rotation);
            const h = groundAt(p.xy[0]+q.x,-p.xy[1]+q.z);
            if (h !== null && Number.isFinite(h)) heights.push(h);
          }
          const gap = Math.max(...heights)-Math.min(...heights);
          if (heights.length!==9 || gap>.06) {
            result.stats.skipped++; result.errors.push(`${p.id}: missing or uneven ground`); continue;
          }
          const ground=Math.max(...heights);
          matrices.push(new Matrix4().compose(new Vector3(p.xy[0],ground-box.min.y,-p.xy[1]),rotation,new Vector3(1,1,1)));
          anchors.push({id:p.id,prop:id,xy:p.xy,yaw_deg:p.yaw_deg,ground,baseGap:gap,size_m:dims});
        }
        if (!matrices.length) continue;
        const group = new Group(); group.name = id; let triangles=0,draws=0;
        const material = (m: Material) => {const copy=m.clone();copy.name=`street_prop_${m.name}`;return copy;};
        asset.traverse(o => {
          if (!(o as Mesh).isMesh) return; const m=o as Mesh;
          const materials=Array.isArray(m.material)?m.material.map(material):material(m.material);
          const inst=new InstancedMesh(m.geometry,materials,matrices.length); inst.name=`${id}:${m.name}`;
          matrices.forEach((matrix,i)=>inst.setMatrixAt(i,matrix.clone().multiply(m.matrixWorld)));
          inst.castShadow=inst.receiveShadow=true; inst.computeBoundingBox();inst.computeBoundingSphere();group.add(inst);
          triangles+=(m.geometry.index?.count??m.geometry.getAttribute('position').count)/3*matrices.length;
          draws+=Array.isArray(materials)?Math.max(1,m.geometry.groups.length):1;
        });
        if (!group.children.length) throw new Error('Empty prop');
        root.add(group);result.anchors.push(...anchors);result.stats.placed+=matrices.length;
        result.stats.triangles+=triangles;result.stats.draws+=draws;
      } catch(e) {result.stats.skipped+=items.length;result.errors.push(`${id}: ${String(e)}`);}
    }
  } catch(e) {result.errors.push(String(e));}
  result.ok=result.errors.length===0;return result;
}
