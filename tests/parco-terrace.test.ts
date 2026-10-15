import { describe, expect, it } from 'vitest';
import { strict as assert } from 'node:assert';
import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Mesh, MeshStandardMaterial, Texture } from 'three';
import { applyLook, classify, LOOK_DEFAULT } from '../src/world/look';
import { LEVEL_BUDGET } from '../src/perf/budget';
import { assertParcoHistoricalFixtures, historicalParcoPath, PARCO_ASSET, PARCO_SHALLOW_SHA256 } from './helpers/parco-stage-fixtures';
import { assertCoreFloorCoverage, assertApertures, assertFloorsAndCeilings, assertPreservation, assertRetainedFragments, assertReturnsAndObliques, encodeGLB, parseGLB, replaceTriangle, triangles } from './helpers/parco-terrace-contract';

const livePath=PARCO_ASSET+'web/parco.glb';
const bytes=readFileSync(livePath),live=parseGLB(bytes),prior=parseGLB(readFileSync(historicalParcoPath('web/parco.glb')));
const components=JSON.parse(readFileSync(historicalParcoPath('source/data/stats.json'),'utf8')).components;
const beforeTriangles=triangles(prior),liveTriangles=triangles(live);
const digest=(b:Buffer)=>createHash('sha256').update(b).digest('hex');
const json=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
const mutant=()=>parseGLB(Buffer.from(bytes));
const load=(b:Buffer)=>new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength) as ArrayBuffer,'');
async function assertCurrentMaterials(b:Buffer) {
  for(const mode of ['day','night'] as const) {
    const {scene}=await load(b),materials=new Map<string,{material:MeshStandardMaterial;mesh:string;before:number[];opacity:number}>();
    scene.traverse(o=>{if(!(o instanceof Mesh))return;for(const raw of Array.isArray(o.material)?o.material:[o.material]) {
      const m=raw as MeshStandardMaterial;if(m.name.startsWith('parco_terrace_'))materials.set(m.name,{material:m,mesh:o.name,before:m.color.toArray(),opacity:m.opacity});
    }});
    assert.equal(materials.size,5,'exact terrace material inventory');
    applyLook(scene,mode,LOOK_DEFAULT,undefined,{map:new Texture(),intensity:1});
    for(const [name,{material:m,mesh,before,opacity}]of materials) {
      const expectedClass=name.includes('glass')?'glass':'wall',rail=name.includes('rail_glass');
      assert.equal(classify(m,mesh),expectedClass,`current material classification ${name}`);
      assert.deepEqual(m.color.toArray(),before,`current material color ${name}`);
      assert.deepEqual(m.emissive.toArray(),[0,0,0],`current material emission ${name}`);
      assert.equal(m.transparent,rail,`current material transparency ${name}`);assert.equal(m.depthWrite,!rail,`current material depthWrite ${name}`);
      assert.equal(m.opacity,opacity,`current material opacity ${name}`);assert.equal(m.envMapIntensity,expectedClass==='glass'?1.6:.5,`current material reflections ${name}`);
      if(rail)assert(Math.abs(opacity-.28)<1e-6);else assert.equal(opacity,1,'opaque reflection proxy must not hide geometry');
    }
  }
}

describe('PARCO current deep terrace: live exported geometry and stage chain',()=>{
  it('pins immutable shallow fixtures and binds canonical/current source/public bytes without substituting a report',()=>{
    assertParcoHistoricalFixtures();expect(digest(prior.bytes)).toBe(PARCO_SHALLOW_SHA256);
    // This identifies the reviewed stage; the remaining tests do not use this
    // hash as a proxy for geometry, and mutations invoke those contracts directly.
    expect(digest(bytes)).toBe('7338ad9fcebf455a82383f938c36d58d817b9a8b0e9b75ff1e3b88ad9e0d9179');
    expect(readFileSync('public/buildings/parco/parco.glb').equals(bytes)).toBe(true);
    expect(readFileSync(PARCO_ASSET+'source/terrace-v1/parco_terrace_candidate.glb').equals(bytes)).toBe(true);
    expect(readFileSync(PARCO_ASSET+'source/terrace-v1/inputs/roof22-corrected-base.glb').equals(prior.bytes)).toBe(true);
    expect(digest(readFileSync(PARCO_ASSET+'source/data/plateau.json'))).toBe('031a66d351a04474ffef5346264e1871f50f6d292bdd898d20bce7ca6bb644a1');
    expect(digest(readFileSync(PARCO_ASSET+'web/viewer.json'))).toBe('8a727c450e07127326a23ecb45364f42787bb86c829bc89a215ed22336ec21be');
  });
  it('preserves every original attribute/material/transform and roof22 byte; only enumerated wall/spandrel/obsolete overlay triangles change',()=>{
    assertPreservation(prior,live,components);
  });
  it('retains the exact source108/152/171 outside-aperture wall and spandrel area without invented fill, gaps or overlap',()=>{
    expect(assertRetainedFragments(beforeTriangles,liveTriangles).length).toBeGreaterThanOrEqual(5);
  });
  it('has actual deep openings in all 3200 geometric aperture probes, independent of glass and color',()=>{
    expect(assertApertures(liveTriangles).count).toBe(3200);
  });
  it('has all 475 floors/soffits at the separate 4F/5F levels rather than a uniform shallow extrusion',()=>{
    expect(assertFloorsAndCeilings(liveTriangles)).toBe(475);
  });
  it('covers the full retained corner-core floor by the actual triangle union after redundant core_base removal',()=>{
    expect(assertCoreFloorCoverage(liveTriangles).uncoveredArea).toBeLessThan(.001);
  });
  it('closes both north returns and all 1920 oblique hollow-shell sightlines',()=>{
    expect(assertReturnsAndObliques(liveTriangles)).toMatchObject({returns:80,obliques:1920});
  });
  it('keeps current mesh/triangle/byte counts and complete manifest honest within the unchanged B budget',()=>{
    const d=live.document,stats={triangles:0,primitives:0,bytes:statSync(livePath).size};
    for(const m of d.meshes)for(const p of m.primitives){stats.triangles+=d.accessors[p.indices].count/3;stats.primitives++;}
    expect(stats).toEqual({triangles:12085,primitives:19,bytes:719392});expect(liveTriangles).toHaveLength(10036);
    expect(stats.triangles).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);expect(stats.primitives).toBeLessThanOrEqual(LEVEL_BUDGET.B.primitives);expect(stats.bytes).toBeLessThanOrEqual(LEVEL_BUDGET.B.bytes);
    const manifest=json(PARCO_ASSET+'manifest.json');expect(manifest.stats).toEqual(stats);
    expect(manifest.source_id).toBe('way/451564412');expect(manifest.plateau_id).toBe('bldg_e199100f-cb89-4a81-8e38-0abee12cb1d4');expect(manifest.level).toBe('B');
    for(const [p,expected]of Object.entries(manifest.files) as [string,{bytes:number;sha256:string}][]) {
      const value=readFileSync(PARCO_ASSET+p);expect(value.length,p).toBe(expected.bytes);expect(digest(value),p).toBe(expected.sha256);
    }
    expect(manifest.files['web/parco.glb'].sha256).toBe(digest(bytes));
    const beforeBounds=beforeTriangles.flatMap(t=>t.points.map(p=>p[2])),afterBounds=liveTriangles.flatMap(t=>t.points.map(p=>p[2]));
    expect(Math.min(...afterBounds)).toBe(Math.min(...beforeBounds));expect(Math.max(...afterBounds)).toBe(Math.max(...beforeBounds));expect(Math.max(...afterBounds)).toBeCloseTo(109.8,4);
  });
  it('parses live bytes in the actual unchanged GLTFLoader/classify/applyLook day/night path',async()=>{
    await assertCurrentMaterials(bytes);
  });
});

describe('PARCO live contracts: negative controls without candidate-hash gating',()=>{
  it('rejects a rollback of repaired roof22 and an off-target original normal edit',()=>{
    const roofRollback=mutant();const oldRoof=parseGLB(readFileSync(PARCO_ASSET+'source/roof-repair-v1/prior.glb'));
    replaceTriangle(roofRollback,0,104,oldRoof.triangle(oldRoof.document.meshes[0].primitives[0].indices,104));
    expect(()=>assertPreservation(prior,roofRollback,components)).toThrow(/original binary edit|roof22/);
    const normalEdit=mutant(),id=normalEdit.document.meshes[1].primitives[0].attributes.NORMAL;
    normalEdit.bytes.writeFloatLE(.5,normalEdit.range(id,0).offset);
    expect(()=>assertPreservation(prior,normalEdit,components)).toThrow(/original binary edit/);
  });
  it('rejects restoring the old opaque front wall even with otherwise valid deep geometry',()=>{
    const wall=mutant(),id=prior.document.meshes[1].primitives[0].indices;
    replaceTriangle(wall,1,195,prior.triangle(id,195));replaceTriangle(wall,1,451,prior.triangle(id,451));
    expect(()=>assertApertures(triangles(wall))).toThrow(/old front shell|cover plane/);
  });
  it('rejects removing all terrace floor triangles despite intact predecessor and saved proof metadata',()=>{
    const floor=mutant(),id=floor.document.meshes[13].primitives[0].indices;
    for(let i=0;i<floor.document.accessors[id].count/3;i++){const first=floor.triangle(id,i)[0];replaceTriangle(floor,13,i,[first,first,first]);}
    // The preservation contract correctly admits changes only in appended data;
    // the separate live geometry contract must still fail this hollow terrace.
    assertPreservation(prior,floor,components);
    expect(()=>assertFloorsAndCeilings(triangles(floor))).toThrow(/missing .*floor|wrong .*floor/);
  });
  it('rejects deleting the core floor despite intact geometry elsewhere',()=>{
    const broken=liveTriangles.filter(t=>!(t.owner==='prototype_terrace_floor'&&t.points.every(p=>Math.abs(p[2]-25.378)<.00003)));
    expect(()=>assertCoreFloorCoverage(broken)).toThrow(/missing current core floor|missing core floor coverage/);
  });
  it('rejects deleting retained outside-aperture wall fragments',()=>{
    const broken=mutant(),id=broken.document.meshes[17].primitives[0].indices,original=broken.triangle(id,0);
    replaceTriangle(broken,17,0,[original[0],original[0],original[0]]);
    expect(()=>assertRetainedFragments(beforeTriangles,triangles(broken))).toThrow(/missing outside-aperture area/);
  });
  it('rejects an alpha trick on the opaque storefront reflection proxy',async()=>{
    const d=structuredClone(live.document),material=d.materials.find((m:any)=>m.name==='parco_terrace_reflective_glass');
    material.alphaMode='BLEND';material.pbrMetallicRoughness.baseColorFactor[3]=.01;
    await expect(assertCurrentMaterials(encodeGLB(d,bytes.subarray(live.binStart)))).rejects.toThrow(/transparency|opacity/);
  });
  it('rejects moving the current 4F floor up while keeping all original bytes unchanged',()=>{
    const floor=mutant(),id=floor.document.meshes[13].primitives[0].attributes.POSITION;
    for(let i=0;i<floor.document.accessors[id].count;i++){
      const at=floor.range(id,i).offset+4;floor.bytes.writeFloatLE(floor.bytes.readFloatLE(at)+.25,at);
    }
    assertPreservation(prior,floor,components);
    expect(()=>assertFloorsAndCeilings(triangles(floor))).toThrow(/floor/);
  });
});
