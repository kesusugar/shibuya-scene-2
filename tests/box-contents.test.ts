import { describe, expect, it } from 'vitest';
import { Group, Mesh, BufferGeometry, Float32BufferAttribute, MeshStandardMaterial, Matrix4, Box3 } from 'three';
import { NodeIO } from '@gltf-transform/core';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { loadBoxContents, shouldLoadBoxContents, type BoxLayout } from '../src/world/boxContents';
import type { BuildingIO } from '../src/world/buildings';

const layout = JSON.parse(readFileSync('assets/street/box-contents/web/layout.json','utf8')) as BoxLayout;
async function geometry(url: string) {
  const group = new Group(), doc = await new NodeIO().read(`assets${url.replace('/box-contents/','/box-contents/web/')}`);
  for (const n of doc.getRoot().listNodes()) for (const p of n.getMesh()?.listPrimitives() ?? []) {
    const g = new BufferGeometry(); g.setAttribute('position',new Float32BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));
    if(p.getIndices()) g.setIndex(Array.from(p.getIndices()!.getArray()!));
    g.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix())); group.add(new Mesh(g,new MeshStandardMaterial()));
  }
  return group;
}
const io = {loadJson:async()=>structuredClone(layout),loadGlb:geometry} as unknown as BuildingIO;
describe('BOX installed contents', () => {
  it('uses one parent and keeps furniture on its proper mounting datum',async()=>{
    const result = await loadBoxContents(io); expect(result.error).toBeUndefined(); expect(result.ok).toBe(true);
    expect(result.stats.parts).toEqual(['counter','wall-monitor','laptop','tkts','portrait-monitor','red-sign','souvenir','tkts-support','soffit-dome','information-header','corner-dome','info-placard','display-spotlights']);
    expect(result.root.position.toArray()).toEqual([layout.origin[0],layout.origin[2],-layout.origin[1]]);
    // Inspect local installed bounds without applying the architecture twice.
    result.root.position.set(0,0,0);result.root.rotation.set(0,0,0);result.root.updateMatrixWorld(true);
    const bounds = Object.fromEntries(result.root.children.map(c=>[c.name.slice(9),new Box3().setFromObject(c)]));
    expect(bounds.counter.min.y).toBeCloseTo(.248,5);
    expect(bounds.laptop.min.y).toBeCloseTo(bounds.counter.max.y,5);
    expect(bounds['wall-monitor'].min.y - bounds.counter.max.y).toBeCloseTo(.04,5);
    expect(bounds.souvenir.min.y).toBeCloseTo(.248,5);
    expect(bounds['tkts-support'].min.y).toBeCloseTo(.248,5);
    expect(bounds.tkts.min.y).toBeCloseTo(bounds['tkts-support'].max.y,5);
    expect(bounds['soffit-dome'].max.y).toBeCloseTo(2.66,5);
    expect(bounds['display-spotlights'].max.y).toBeCloseTo(2.584,5);
    expect(bounds['information-header'].min.y).toBeGreaterThan(2.30);
    expect(-bounds['information-header'].min.z).toBeLessThan(-.68);
    expect(bounds['info-placard'].max.x).toBeLessThan(bounds.counter.max.x);
    expect(bounds['info-placard'].max.y).toBeLessThan(bounds.counter.max.y);
    expect(-bounds['info-placard'].min.z).toBeLessThan(.52);
    // Rear of monitor clears the frontmost face of the reused wood sample.
    expect(-bounds['wall-monitor'].min.z).toBeLessThan(1.41 + .211 * .92);
    for(const [id,b] of Object.entries(bounds).filter(([id])=>!['soffit-dome','information-header','corner-dome','info-placard','display-spotlights'].includes(id))) {
      expect(b.min.y,id).toBeGreaterThanOrEqual(.24799);
      expect(b.max.y,id).toBeLessThanOrEqual(2.58401);
      expect(b.min.x,id).toBeGreaterThan(-6.0);expect(b.max.x,id).toBeLessThan(6.0);
      expect(-b.min.z,id).toBeLessThan(1.706); // rear closure inner face
      expect(-b.max.z,id).toBeGreaterThan(.1); // glazing/door plane -.514, keep entry approach clear
    }
    if(bounds.souvenir) expect(bounds['wall-monitor'].min.z).toBeGreaterThan(bounds.souvenir.min.z);
  });
  it('rejects null transforms and duplicate parts instead of placing them at the origin',async()=>{
    const invalid = structuredClone(layout); (invalid.parts[0].position as unknown[])[0] = null;
    const result = await loadBoxContents({...io,loadJson:async()=>invalid} as unknown as BuildingIO);
    expect(result.ok).toBe(false);expect(result.root.children).toHaveLength(0);
    const duplicate = structuredClone(layout);duplicate.parts.push(duplicate.parts[0]);
    expect((await loadBoxContents({...io,loadJson:async()=>duplicate} as unknown as BuildingIO)).error).toContain('Duplicate');
  });
  it('preserves the accepted BOX architecture byte for byte',()=>{
    expect(createHash('sha256').update(readFileSync('assets/buildings/shibu-hachi-box/web/shibu-hachi-box.glb')).digest('hex')).toBe('c1b262ee107e8b46baad917f30aff885420a8ac611f071b67469b542a18f7a5e');
  });
});

it('skips content requests for street off, contents off and absent BOX',()=>{
 for(const [query,box,expected] of [['',true,true],['street=off',true,false],['boxcontents=off',true,false],['',false,false]] as const)
  expect(shouldLoadBoxContents(new URLSearchParams(query),box)).toBe(expected);
});
it('starts all independent requests before any resolves and commits in layout order',async()=>{
 const callbacks: (()=>void)[]=[];
 const task=loadBoxContents({...io,loadGlb:async(url:string)=>new Promise<Group>((resolve)=>callbacks.push(()=>{void geometry(url).then(resolve);} ))} as unknown as BuildingIO);
 await Promise.resolve(); expect(callbacks).toHaveLength(layout.parts.length);
 for(const resolve of callbacks.reverse()) resolve();
 const result=await task;expect(result.ok).toBe(true);expect(result.stats.parts).toEqual(layout.parts.map(p=>p.id));
});
it('a failed parallel request publishes neither partial parts nor success',async()=>{
 const result=await loadBoxContents({...io,loadGlb:async(url:string)=>{if(url.includes('laptop'))throw Error('HTTP failure');return geometry(url);}} as unknown as BuildingIO);
 expect(result.ok).toBe(false);expect(result.root.children).toHaveLength(0);expect(result.stats.parts).toEqual([]);expect(result.error).toContain('HTTP failure');
});
