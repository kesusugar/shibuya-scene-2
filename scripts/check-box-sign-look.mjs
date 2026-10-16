// Built normal street; same cameras before/after. No production hooks or FPS reads.
import {chromium} from 'playwright';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const log={};
try{
 for(const [name,pose] of Object.entries({roof:'18,-48,4.1,25.1,-46.7,3.45,50',clock:'23,-36,2.1,24.25,-41.15,1.75,48'})){
  for(const pass of ['normal','class']){
   const page=await browser.newPage({viewport:{width:1000,height:650}}),errors=[];
   await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
   page.on('pageerror',e=>errors.push(e.message));
   page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
   const url=base+'/?capture&time=day&pose='+pose+(pass==='class'?'&pass=class':'');
   await page.goto(url);await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:300000});
   const state=await page.evaluate(()=>({failed:window.__viewer.failed,box:window.__viewer.stats['shibu-hachi-box']}));
   assert.deepEqual(state.failed,[]);assert.deepEqual(state.box.layerErrors,[]);assert.equal(state.box.layers.length,6);
   if(process.argv.includes('--expect-signs')){
    const expected=JSON.parse(readFileSync('assets/buildings/shibu-hachi-box/source/exterior-signs/placement.json','utf8')).components.map(c=>c.layer).sort();
    assert.deepEqual([...state.box.layers].sort(),expected);
   }
   for(const mode of pass==='normal'?['day','night','day-return']:['class']){
    if(mode==='night'||mode==='day-return')await page.locator(mode==='night'?'#btn-night':'#btn-day').dispatchEvent('click');
    await page.waitForTimeout(1200);
    await page.screenshot({path:`${out}/${name}-${mode}.png`,timeout:300000});
   }
   if(pass==='normal')assert(readFileSync(`${out}/${name}-day.png`).equals(readFileSync(`${out}/${name}-day-return.png`)),'day/night/day did not restore the initial frame');
   assert.deepEqual(errors,[]);log[name+'-'+pass]={pose,state,errors};await page.close();
   console.log(name,pass,'OK');
  }
 }
 writeFileSync(out+'/checks.json',JSON.stringify(log,null,2)+'\n');
}finally{await browser.close();}
