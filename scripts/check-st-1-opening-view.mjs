// Additional oblique check: PR81's oblique camera is partially occluded by an unchanged building.
import {chromium} from 'playwright';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2),pose='99,-15,3.3,90,-25,1.8,48';
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}),log={};
try{
 for(const version of ['before','after']){
  const page=await browser.newPage({viewport:{width:1100,height:750}}),errors=[];
  await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
  if(version==='before')await page.route('**/buildings/station-north/station-north.glb',r=>r.fulfill({body:readFileSync('assets/buildings/station-north/source/st-1-opening/station-north-pr81.glb'),contentType:'model/gltf-binary'}));
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.goto(base+'/?capture&time=day&pose='+pose);
  await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:300000});
  await page.waitForTimeout(2500);
  const state=await page.evaluate(()=>({failed:window.__viewer.failed,station:window.__viewer.stats['station-north'],camera:window.__viewer.cameraPos()}));
  assert.deepEqual(state.failed,[]);assert.deepEqual(state.station.layerErrors,[]);assert.deepEqual(errors,[]);
  await page.evaluate(()=>{window.requestAnimationFrame=()=>0;});await page.waitForTimeout(500);
  await page.screenshot({path:out+'/'+version+'.png',timeout:300000});
  log[version]={pose,state,errors,baselineBodyOnly:version==='before'};
  await page.close();console.log(version,'OK');
 }
 writeFileSync(out+'/checks.json',JSON.stringify(log,null,2)+'\n');
}finally{await browser.close();}
