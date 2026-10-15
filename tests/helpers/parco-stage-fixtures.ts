import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
export const PARCO_ASSET='assets/buildings/parco/';
export const PARCO_SHALLOW_SHA256='7dbb2e71338da1d3a5a6db6ec52ec38235f07ba5adbbd7b0585f6bcb15d372cd';
export const historicalParcoPath=(p:string)=>PARCO_ASSET+({'web/parco.glb':'source/terrace-v1/inputs/roof22-corrected-base.glb','source/data/stats.json':'source/podium-v1/stats.json','manifest.json':'source/podium-v1/manifest.json'}[p]??p);
export const assertParcoHistoricalFixtures=()=>{for(const [p,h] of Object.entries({'web/parco.glb':PARCO_SHALLOW_SHA256,'source/data/stats.json':'3b82574c0445f515daacf96f3216d84a9ee55a3f0efad96fa5634940dfedfc47'}))assert.equal(createHash('sha256').update(readFileSync(historicalParcoPath(p))).digest('hex'),h,p);};
