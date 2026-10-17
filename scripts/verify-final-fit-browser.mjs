import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const [base,out]=process.argv.slice(2);mkdirSync(out,{recursive:true});
const browser=await chromium.launch({args:['--ignore-gpu-blocklist']});const results={};
try {
 for(const [name,query] of [['normal',''],['street-off','street=off'],['contents-off','boxcontents=off'],['no-box','buildings=plaza-kiosk'],['failed','']]){
  if(process.env.CASES && !process.env.CASES.split(',').includes(name))continue;
  const page=await browser.newPage({viewport:{width:1000,height:750}}),requests=[],errors=[];
  page.on('request',r=>{if(r.url().includes('/street/box-contents/'))requests.push(new URL(r.url()).pathname);});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
  if(name==='failed')await page.route('**/street/box-contents/laptop.glb',r=>r.fulfill({status:503,body:'Intentional regression failure'}));
  await page.goto(`${base}/?capture&q=medium&time=day&pose=21.15,-47.315,2.289,25.9,-46.57,1.69,52&${query}`);
  await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:300000});
  await page.evaluate(()=>window.__viewer.freezeFrame());
  const state=await page.evaluate(()=>({contents:window.__viewer.boxContents,street:window.__viewer.street,stats:window.__viewer.stats,status:document.querySelector('#status').textContent,camera:window.__viewer.cameraState()}));
  assert.deepEqual(errors,[]);
  if(['street-off','contents-off','no-box'].includes(name)){assert.deepEqual(requests,[]);assert.equal(state.contents,'off');}
  else if(name==='normal'){assert.equal(state.contents.ok,true);assert.equal(state.contents.parts.length,13);assert.equal(requests.filter(x=>x.endsWith('.glb')).length,13);}
  else{assert.equal(state.contents.ok,false);assert.deepEqual(state.contents.parts,[]);assert.match(state.contents.error,/503/);}
  if(name==='street-off')assert.ok(state.stats['shibu-hachi-box']);
  await page.screenshot({path:`${out}/${name}.png`,timeout:300000});
  results[name]={query,requests,errors,state};writeFileSync(`${out}/regression.json`,JSON.stringify(results,null,2)+'\n');
  if(name==='normal'){
   const views=[
    ['accessories-night',[21.5,-38,2.8,24.3,-41.1,2.8,48],'night'],
    ['dome-detail',[21.7,-39,2.85,22.72,-41.0,3.10,20],'day'],
    ['roof-corner',[27.7,-37.8,3.2,25.635,-40.064,3.25,26],'day'],
    ['foliage-0',[15,-53,1.6,12.5,-50,1.2,52],'day'],
    ['foliage-1',[15.3,-52.7,1.6,12.5,-50,1.2,52],'day'],
    ['foliage-2',[15.6,-52.4,1.6,12.5,-50,1.2,52],'day'],
   ];const cameras={};
   for(const [id,pose,time] of views){
    if(process.env.DETAILS && !process.env.DETAILS.split(',').includes(id))continue;
    await page.evaluate(({pose,time})=>window.__viewer.capturePose(pose,time),{pose,time});
    await page.waitForTimeout(500);await page.evaluate(()=>window.__viewer.freezeFrame());
    cameras[id]=await page.evaluate(()=>window.__viewer.cameraState());
    await page.screenshot({path:`${out}/${id}.png`,timeout:300000});
   }
   writeFileSync(`${out}/detail-cameras.json`,JSON.stringify(cameras,null,2)+'\n');
  }
  console.log(name,'ok');await page.close();
 }
}finally{await browser.close();}
