import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3 } from 'three';

const dir='assets/buildings/shibu-hachi-box';
const report=JSON.parse(readFileSync(`${dir}/source/placement-and-build.json`,'utf8'));
const basis=new Matrix4().makeRotationX(-Math.PI/2);
const inverse=basis.clone().multiply(new Matrix4().set(...report.inverse_matrix_rows.flat() as Parameters<Matrix4['set']>)).multiply(basis.clone().invert());
type Tri={material:string; points:Vector3[]};
async function triangles(path:string, transform=new Matrix4()):Promise<Tri[]> {
  const result:Tri[]=[];
  for(const node of (await new NodeIO().read(path)).getRoot().listNodes()) {
    const matrix=transform.clone().multiply(new Matrix4().fromArray(node.getWorldMatrix()));
    for(const p of node.getMesh()?.listPrimitives()??[]) {
      const positions=p.getAttribute('POSITION')!, indices=p.getIndices();
      for(let i=0;i<(indices?.getCount()??positions.getCount());i+=3) {
        result.push({material:p.getMaterial()!.getName().replace(/\.\d+$/,''),points:[0,1,2].map(j=>new Vector3().fromArray(positions.getElement(indices?indices.getScalar(i+j):i+j,[])).applyMatrix4(matrix))});
      }
    }
  }
  return result;
}
const same=(a:Tri,b:Tri)=>a.material===b.material && a.points.every(p=>b.points.some(q=>p.distanceTo(q)<.00002));
describe('BOX-1 shipped geometry',()=>{
  it('preserves the main slab and inferred rear closure, not just the material batch name',async()=>{
    const source=await triangles('assets/street/props/incoming/shibu_hachi_box_architecture_reference/output/shibu_hachi_box.glb');
    // GLB Y-up: main slab z=-1.786..+.680, rear closure z=-1.766..-1.706.
    const mineral=source.filter(t=>t.material==='03_Pale_mineral_platform');
    const parent=mineral.map((_,i)=>i), seen=new Map<string,number>();
    const find=(i:number):number=>parent[i]===i?i:(parent[i]=find(parent[i]));
    mineral.forEach((t,i)=>t.points.forEach(p=>{const key=p.toArray().map(n=>n.toFixed(6)).join(',');const j=seen.get(key);if(j!==undefined)parent[find(i)]=find(j);else seen.set(key,i);}));
    const components=new Map<number,Tri[]>();mineral.forEach((t,i)=>components.set(find(i),[...(components.get(find(i))??[]),t]));
    const protectedTriangles=[...components.values()].filter(ts=>Math.max(...ts.flatMap(t=>t.points.map(p=>p.z)))<=.68001 && Math.min(...ts.flatMap(t=>t.points.map(p=>p.z)))< -1.7).flat();
    expect(protectedTriangles).toHaveLength(120);
    const shipped=await triangles(`${dir}/web/shibu-hachi-box.glb`,inverse);
    for(const tri of protectedTriangles) expect(shipped.some(t=>same(tri,t)),'protected triangle missing').toBe(true);
  });
  it('contains every terrace triangle exactly once with one rigid local fit',async()=>{
    const fit=new Matrix4().makeTranslation(-.10478019714355469,-.16432876884937286,1.3359999656677246);
    const terrace=await triangles(`${dir}/source/terrace-v001/shibu_hachi_front_terrace_candidate_v001.glb`,fit);
    expect(terrace).toHaveLength(8440);
    const shipped=await triangles(`${dir}/web/shibu-hachi-box.glb`,inverse);
    // Index by material and coarse centroid for bounded candidate lookup.
    const key=(t:Tri)=>t.material+':'+t.points.reduce((s,p)=>s.add(p),new Vector3()).multiplyScalar(1/3).toArray().map(n=>Math.floor(n*10)).join(',');
    const groups=new Map<string,Tri[]>();for(const t of shipped){const k=key(t);groups.set(k,[...(groups.get(k)??[]),t]);}
    for(const tri of terrace) {
      const centre=tri.points.reduce((s,p)=>s.add(p),new Vector3()).multiplyScalar(1/3);
      const cell=centre.toArray().map(n=>Math.floor(n*10));
      const candidates:Tri[]=[];
      for(const x of [-1,0,1])for(const y of [-1,0,1])for(const z of [-1,0,1])candidates.push(...(groups.get(tri.material+':'+[cell[0]+x,cell[1]+y,cell[2]+z].join(','))??[]));
      expect(candidates.filter(t=>same(tri,t))).toHaveLength(1);
    }
  });
  it('pins the saved asset and keeps world placement out of viewer height adjustment',()=>{
    const hash=createHash('sha256').update(readFileSync(`${dir}/web/shibu-hachi-box.glb`)).digest('hex');
    expect(hash).toBe(report.sha256);
    expect(report.scale).toEqual([1,1,1]);
    expect(JSON.parse(readFileSync(`${dir}/web/viewer.json`,'utf8')).groundElevationTP).toBe(15);
    expect(report.ground_fit.r3_top_gap_m).toBeCloseTo(.005);
    expect(report.selectively_cut).toHaveLength(5);
  });
});
