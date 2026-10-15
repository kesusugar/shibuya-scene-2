import {it,expect} from 'vitest';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {Mesh,MeshStandardMaterial} from 'three';
import {loadBuilding,applyEmissive} from '../src/world/buildings';
import {classify,applyLook,LOOK_DEFAULT} from '../src/world/look';
import {LEVEL_BUDGET} from '../src/perf/budget';
const A='assets/buildings/mark-city/';
const load=async(path:string)=>{const b=readFileSync(path);return (await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength), '')).scene;};
it('loads the exact delivered cumulative revision at the unchanged zero offset and B budget',async()=>{
 const b=readFileSync(A+'web/mark-city.glb');expect(createHash('sha256').update(b).digest('hex')).toBe('8dc763dcd1e242de07f7846ba7789a40252c6efb0eed88d531faf6d1c3b4cd5d');
 const r=await loadBuilding('mark-city',{loadGlb:async()=>load(A+'web/mark-city.glb'),loadJson:async(url)=>JSON.parse(readFileSync(A+'web/'+url.split('/').pop(),'utf8'))});expect(r.ok).toBe(true);if(!r.ok)throw Error(r.error);expect(r.root.position.y).toBe(0);expect(r.layerErrors).toEqual([]);expect(r.stats.triangles).toBe(25312);expect(r.stats.meshes).toBe(28);expect(r.stats.triangles).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);expect(r.stats.meshes).toBeLessThanOrEqual(LEVEL_BUDGET.B.primitives);expect(b.length).toBeLessThanOrEqual(LEVEL_BUDGET.B.bytes);
});
it('keeps cap panel and frame opaque, wall-classified and non-emissive under current day/night runtime',async()=>{
 for(const mode of ['day','night'] as const){const root=await load(A+'web/mark-city.glb');applyEmissive(root,{});applyLook(root,mode,LOOK_DEFAULT,{});let count=0;root.traverse(o=>{if(!(o instanceof Mesh))return;for(const m of Array.isArray(o.material)?o.material:[o.material])if(['west_cap_panel_opaque','west_cap_frame'].includes(m.name)){count++;expect(classify(m,o.name,{})).toBe('wall');const s=m as MeshStandardMaterial;expect(s.transparent).toBe(false);expect(s.opacity).toBe(1);expect(s.emissive.r+s.emissive.g+s.emissive.b).toBe(0);expect(s.map).toBeNull();}});expect(count).toBe(2);}
});
