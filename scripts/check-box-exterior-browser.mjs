// Fixed-view temporal check, separate from FPS measurement. No source/asset writes.
import {chromium} from 'playwright';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2),browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const expected=JSON.parse(readFileSync('assets/buildings/shibu-hachi-box/source/exterior-signs/placement.json','utf8')).components.map(c=>c.layer).sort();
try{
 const page=await browser.newPage({viewport:{width:1400,height:600}}),errors=[];
 await page.route('**/favicon.ico',r=>r.fulfill({status:204}));page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/?capture&time=day&pose=18,-48,4.1,25.1,-46.7,3.45,50');
 await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:300000});await page.waitForTimeout(2500);
 const a=await page.screenshot({timeout:300000});await page.waitForTimeout(1000);const b=await page.screenshot({timeout:300000});
 const state=await page.evaluate(()=>({box:window.__viewer.stats['shibu-hachi-box'],failed:window.__viewer.failed}));
 assert.deepEqual(errors,[]);assert.deepEqual(state.failed,[]);assert.deepEqual(state.box.layerErrors,[]);assert.equal(state.box.layers.length,6);
 assert.deepEqual([...state.box.layers].sort(),expected);
 const same=a.equals(b),sha=bytes=>createHash('sha256').update(bytes).digest('hex');
 writeFileSync(out,JSON.stringify({method:'Two independent PNG captures one second apart, renderer not frozen, fixed roof-sign camera; no FPS read or benchmark.',samePixelsAndEncoding:same,firstPNG:sha(a),secondPNG:sha(b),state,errors},null,2)+'\n');
 assert(same,'Fixed roof view changed between frames; inspect before claiming no flicker');console.log('Fixed roof-sign frames identical; six layers loaded');
}finally{await browser.close();}
