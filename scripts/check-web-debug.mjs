import {chromium} from 'playwright';
import {mkdirSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2);mkdirSync(out,{recursive:true});
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 let page=await browser.newPage({viewport:{width:1280,height:800}});const errors=[];
 await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'?debug');
 await page.waitForFunction(()=>window.__startupDebug?.state.firstFrameMs!==null&&window.__viewer?.ready,null,{timeout:400000});
 let state=await page.evaluate(()=>window.__startupDebug.snapshot());
 assert.deepEqual(errors,[]);assert.deepEqual(state.errors,[]);assert.ok(state.readyMs>0);assert.ok(state.firstFrameMs>=state.readyMs);
 assert.ok(state.assets.length>30);assert.ok(state.assets.every(a=>a.status==='ok'));assert.ok(state.resources.some(r=>r.url.includes('/shibuya-scene-2/buildings/')));
 assert.equal(await page.evaluate(()=>Object.keys(window.__viewer.stats).length),28);
 await page.screenshot({path:out+'/normal.png',timeout:400000});
 const downloadPromise=page.waitForEvent('download');await page.locator('#debug-download').click();const download=await downloadPromise;await download.saveAs(out+'/download.json');
 writeFileSync(out+'/normal.json',JSON.stringify(state,null,2));console.log('normal',state.readyMs,state.firstFrameMs,state.assets.length);
 await page.evaluate(()=>{window.dispatchEvent(new ErrorEvent('error',{message:'QA runtime failure'}));window.dispatchEvent(new PromiseRejectionEvent('unhandledrejection',{promise:Promise.resolve(),reason:new Error('QA promise failure')}));});
 state=await page.evaluate(()=>window.__startupDebug.snapshot());assert.ok(state.errors.some(e=>e.message.includes('QA runtime')));assert.ok(state.errors.some(e=>e.message.includes('QA promise')));
 await page.close();
 // A missing application bundle must still leave a usable diagnostic UI.
 page=await browser.newPage({viewport:{width:800,height:700}});
 await page.route('**/assets/*.js',r=>r.abort());await page.goto(base+'?debug');
 await page.waitForFunction(()=>window.__startupDebug?.state.errors.length>0);
 state=await page.evaluate(()=>window.__startupDebug.snapshot());assert.equal(state.readyMs,null);
 await page.screenshot({path:out+'/module-failure.png'});writeFileSync(out+'/module-failure.json',JSON.stringify(state,null,2));await page.close();
 // An unavailable GLB must be reported while unrelated buildings keep rendering.
 page=await browser.newPage({viewport:{width:1000,height:750}});
 await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
 await page.route('**/ground/core/ground_core.glb',r=>r.fulfill({status:503,body:'QA asset unavailable'}));
 await page.goto(base+'?debug&q=low');await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:400000});
 state=await page.evaluate(()=>window.__startupDebug.snapshot());assert.ok(state.errors.some(e=>e.message.includes('ground_core.glb')));assert.ok(state.assets.some(a=>a.url.includes('ground_core.glb')&&a.status==='error'));assert.ok(state.readyMs>0);
 await page.screenshot({path:out+'/asset-failure.png',timeout:400000});writeFileSync(out+'/asset-failure.json',JSON.stringify(state,null,2));
 await page.close();console.log('runtime, promise, module and GLB failure checks passed');
}finally{await browser.close();}
