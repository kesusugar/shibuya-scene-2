// Same normal street and camera; no production debug hook or FPS reads.
import {chromium} from 'playwright';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2),baseline=process.argv.includes('--baseline');
const config=JSON.parse(readFileSync('assets/buildings/station-north/source/st-1/placement.json','utf8'));
const expected=baseline?[]:config.components.map(c=>c.layer).sort();
const pose='114,-18,3.5,90,-25,2.4,48';
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}),log={};
try{
 for(const pass of ['normal','class']){
  const page=await browser.newPage({viewport:{width:1100,height:750}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
  await page.goto(base+'/?capture&time=day&pose='+pose+(pass==='class'?'&pass=class':''));
  await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:300000});
  const state=await page.evaluate(()=>({failed:window.__viewer.failed,station:window.__viewer.stats['station-north'],notice:document.querySelector('#provisional').textContent}));
  assert.deepEqual(state.failed,[]);assert.deepEqual(state.station.layerErrors,[]);assert.deepEqual([...state.station.layers].sort(),expected);
  let first;
  for(const mode of pass==='normal'?['day','night','day-return']:['class']){
   if(mode==='night'||mode==='day-return')await page.locator(mode==='night'?'#btn-night':'#btn-day').dispatchEvent('click');
   await page.waitForTimeout(1500);const bytes=await page.screenshot({path:out+'/front-'+mode+'.png',timeout:300000});
   if(mode==='day'){
    first=bytes;await page.waitForTimeout(1000);
    const second=await page.screenshot({path:out+'/front-day-second.png',timeout:300000});
    assert(first.equals(second),'Fixed front view changed between unfrozen frames');
   }
   if(mode==='day-return')assert(first.equals(bytes),'Day/night/day changed the restored day frame');
  }
  assert.deepEqual(errors,[]);log[pass]={pose,baseline,state,errors,dayNightDayRestored:pass==='normal'?true:undefined,unfrozenFramesOneSecondApartIdentical:pass==='normal'?true:undefined};
  await page.close();console.log(pass,'OK');
 }
 writeFileSync(out+'/checks.json',JSON.stringify(log,null,2)+'\n');
}finally{await browser.close();}
