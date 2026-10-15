// Runtime clearance checks against actual scene meshes, not object bounding boxes.
import {chromium} from 'playwright';
import {writeFileSync} from 'node:fs';
import {dirname} from 'node:path';
import assert from 'node:assert/strict';
const [base,out]=process.argv.slice(2);
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try {
 const page=await browser.newPage({viewport:{width:1000,height:700}});
 await page.route('**/src/main.ts',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:await res.text()+'\nwindow.__placementQA={scene,controls,get hints(){return loaded[0].hints;},setTime};'});});
 await page.goto(base+'/?capture');await page.waitForFunction(()=>window.__viewer?.ready,null,{timeout:400000});
 const result=await page.evaluate(async()=>{
  const {Raycaster,Vector3}=await import('/node_modules/.vite/deps/three.js');
  const {scene,controls}=window.__placementQA,props=scene.getObjectByName('street:props');
  const tactile=scene.children.filter(o=>o.name.startsWith('street:tactile'));
  const others=controls.obstacles.filter(o=>o!==props),ray=new Raycaster();
  const checks=window.__viewer.props.anchors.map(a=>{
   const [x,y]=a.xy,r=Math.hypot(a.size_m[0],a.size_m[1])/2;
   const tactileHits=[],nearby=[];
   for(const dx of [-r,0,r])for(const dy of [-r,0,r]){
    ray.set(new Vector3(x+dx,a.ground+2,-y+dy),new Vector3(0,-1,0));ray.far=3;
    if(ray.intersectObjects(tactile,true).length)tactileHits.push([dx,dy]);
   }
   for(let i=0;i<16;i++)for(const h of [.1,Math.min(.5,a.size_m[2]/2)]){
    const direction=new Vector3(Math.cos(i*Math.PI/8),0,Math.sin(i*Math.PI/8));
    ray.set(new Vector3(x,a.ground+h,-y),direction);ray.far=r+.1;
    const hit=ray.intersectObjects(others,true)[0];if(hit)nearby.push({name:hit.object.name,distance:hit.distance});
   }
   ray.set(new Vector3(x-2,a.ground+.25,-y),new Vector3(1,0,0));ray.far=3;
   const hits=ray.intersectObject(props,true).map(h=>({name:h.object.name,distance:h.distance}));
   const saved=controls.obstacles;controls.setObstacles([props]);
   const isolatedWalk=window.__viewer.walkTest(x-2,y,1,0,16,.25);controls.setObstacles(saved);
   return {...a,tactileHits,nearby,ownCollisionHits:hits,isolatedWalk,walkInto:window.__viewer.walkTest(x-2,y,1,0,16,.25)};
  });
  return {failed:window.__viewer.failed,props:window.__viewer.props,checks,bypassCones:window.__viewer.walkTest(-10,-58,0,-1,16,.25)};
 });
 writeFileSync(out,JSON.stringify(result,null,2));
 assert.deepEqual(result.failed,[]);assert.equal(result.props.placed,6);
 for(const c of result.checks){assert.ok(c.baseGap<=.06,c.id);assert.deepEqual(c.tactileHits,[],c.id);assert.deepEqual(c.nearby,[],c.id);assert.ok(c.ownCollisionHits.length,c.id);assert.ok(c.isolatedWalk.stoppedAt,c.id);}
 assert.equal(result.bypassCones.stoppedAt,null);assert.equal(result.bypassCones.path.length,16);
 console.log('6 ground/clearance/collision checks and cone bypass passed');
 for(const [name,night,pose] of [['rear',false,[13,-55,2.2,11.5,-50,1,55]],['notice-night',true,[2,-20,2,8,-31,1,60]]]){
  await page.evaluate(({night,pose})=>{const q=window.__placementQA;q.setTime(night?'night':'day');q.controls.poseView(pose.slice(0,3),pose.slice(3,6),pose[6],q.hints);},{night,pose});
  await page.waitForTimeout(1200);await page.screenshot({path:dirname(out)+'/'+name+'.png',timeout:400000});console.log(name);
 }

}finally{await browser.close();}
