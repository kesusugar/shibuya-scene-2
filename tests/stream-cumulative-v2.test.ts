import {it,expect} from 'vitest';
import {readFileSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {NodeIO} from '@gltf-transform/core';
import {ASSET_LEVEL,LEVEL_BUDGET} from '../src/perf/budget';
const base='assets/buildings/stream/';
it('Stream cumulative-v2 matches pinned runtime, metadata and unchanged level budget',async()=>{
 const p=base+'web/stream.glb',raw=readFileSync(p),root=(await new NodeIO().read(p)).getRoot();
 expect(createHash('sha256').update(raw).digest('hex')).toBe('e03535bbe29f29524354f76cb8f066b30072fe355abda503d2ddeb8f70f96b32');
 let triangles=0,primitives=0;for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){primitives++;triangles+=p.getIndices()!.getCount()/3;expect(p.getMaterial()!.getBaseColorTexture()).toBeNull();}
 expect({triangles,primitives,bytes:statSync(p).size}).toEqual({triangles:32538,primitives:8,bytes:2022104});
 expect(ASSET_LEVEL.stream).toBe('B');const budget=LEVEL_BUDGET[ASSET_LEVEL.stream];expect(triangles).toBeLessThanOrEqual(budget.triangles);expect(primitives).toBeLessThanOrEqual(budget.primitives);expect(raw.length).toBeLessThanOrEqual(budget.bytes);
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));expect(stats.triangles).toBe(triangles);expect(stats.bytes).toBe(raw.length);expect(stats.datum_tp_m).toBe(15);expect(stats.missing_pavement_samples).toBe(0);expect(stats.pavement_samples).toHaveLength(144);
});
