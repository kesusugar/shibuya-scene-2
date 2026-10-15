// Same-camera placement evidence. Source/asset edits must finish before capture.
import {chromium} from 'playwright';
import {mkdirSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2);mkdirSync(out,{recursive:true});
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1000,height:700}}),errors=[];
 await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
 await page.route('**/src/main.ts',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:await res.text()+'\nwindow.__placementQA={scene,controls,get buildings(){return loaded;}};'});});
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
 await page.goto(base+'/?capture&time='+(process.env.TIME||'day')+(process.env.EXTRA?'&'+process.env.EXTRA:''));
 await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:400000});
 const state=await page.evaluate(()=>window.__viewer);assert.deepEqual(state.failed,[]);assert.equal(state.exterior.ok,true);assert.equal(state.ground.ok,true);
 if(state.props!=='off') {assert.equal(state.props.ok,true);assert.equal(state.props.placed,6);}
 const log={errors,views:{}};
 for(const [name,pose]of Object.entries({rear:[13,-55,2.2,11.5,-50,1,55],entry:null,notice:[2,-20,2,8,-31,1,60],hachiko:[4,-47,3,13,-51,1.1,60],station:[-8,-49,2,-8,-62,1.1,65],overview:[-5,-95,95,-30,-15,12,58]})){
  if(process.env.VIEWS&&!process.env.VIEWS.split(',').includes(name))continue;
  if(pose)await page.evaluate(p=>{const q=window.__placementQA;q.controls.poseView(p.slice(0,3),p.slice(3,6),p[6],q.buildings[0].hints);},pose);
  await page.waitForTimeout(1200);await page.screenshot({path:`${out}/${name}.png`,timeout:400000});log.views[name]=pose;console.log(name);
 }
 log.viewer=await page.evaluate(()=>window.__viewer);log.status=await page.locator('#status').textContent();
 log.probes=await page.evaluate(()=>[[10.413,-52.791],[15.819,-49.007],[8,-31],[-12,-61],[-8,-61],[-4,-61]].map(([x,y])=>({xy:[x,y],ground:window.__placementQA.controls.groundAt(x,-y,5)})));
 writeFileSync(out+'/capture.json',JSON.stringify(log,null,2));assert.deepEqual(errors,[]);assert.deepEqual(log.viewer.failed,[]);assert.equal(log.viewer.ground.ok,true);
}finally{await browser.close();}
