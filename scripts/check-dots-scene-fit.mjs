// Full-scene QA for the merged dots assets. No model or production source edits.
// Run after npm run build, against Vite dev: node scripts/check-dots-scene-fit.mjs <base> <out>
// The Playwright-only hook reads the actual loaded scene; it is never shipped.
import { chromium } from 'playwright';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const [base = 'http://127.0.0.1:5230', out = 'evidence/dots-scene-fit'] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const recorded = {};
for (const [id,file,key] of [
  ['west-block','ground_measurements.json','frontage_samples'],
  ['ekimae','stats.json','frontage_samples'],
  ['daiichi-kangin','recorded_ground.json','pavement_samples'],
]) recorded[id]=JSON.parse(readFileSync(`assets/buildings/${id}/source/data/${file}`,'utf8'))[key];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
  await page.route('**/favicon.ico', r => r.fulfill({ status: 204 }));
  await page.route('**/src/main.ts', async route => {
    const response = await route.fetch();
    const body = await response.text();
    await route.fulfill({ response, body: body + '\nwindow.__fit = {scene, camera, controls, io, get buildings() {return loaded;}};\n' });
  });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`); });
  await page.goto(`${base}/?capture&time=day`);
  await page.waitForFunction(() => window.__viewer?.ready, null, { timeout: 400000 });
  const result = await page.evaluate(async recorded => {
    const { Box3, Vector3, Raycaster } = await import('/node_modules/.vite/deps/three.js');
    const { scene, controls, buildings } = window.__fit;
    scene.updateMatrixWorld(true);
    const ground = ['ground:core', 'ground:exterior', 'ground:extension'].map(n => scene.getObjectByName(n)).filter(Boolean);
    const ray = new Raycaster(); const p = new Vector3();
    const bounds = o => { const b = new Box3().setFromObject(o); return { min: b.min.toArray(), max: b.max.toArray(), size: b.getSize(new Vector3()).toArray() }; };
    const assets = {};
    for (const id of ['west-block', 'daiichi-kangin', 'ekimae', 'center244']) {
      const b = buildings.find(b => b.id === id); const box = new Box3().setFromObject(b.root);
      const samples = new Map();
      b.root.traverse(m => {
        if (!m.isMesh) return;
        const a = m.geometry.getAttribute('position');
        for (let i = 0; i < a.count; i++) {
          p.fromBufferAttribute(a, i).applyMatrix4(m.matrixWorld);
          if (p.y > 1.5) continue;
          const key = `${p.x.toFixed(2)},${p.z.toFixed(2)}`;
          if (!samples.has(key) || samples.get(key).y > p.y) samples.set(key, {x:p.x,y:p.y,z:p.z,mesh:m.name});
        }
      });
      const feet = [...samples.values()].map(p => {
        ray.set(new Vector3(p.x, 5, p.z), new Vector3(0,-1,0));
        const h = ray.intersectObjects(ground,true)[0];
        return {plan:[p.x,-p.z,p.y],mesh:p.mesh,ground:h?.point.y??null,gap:h?p.y-h.point.y:null,surface:h?.object.name??null};
      });
      const overlaps = buildings.filter(o=>o.id!==id).flatMap(o=> {
        const intersection=box.clone().intersect(new Box3().setFromObject(o.root));
        return intersection.isEmpty()?[]:[{id:o.id,overlapSize:intersection.getSize(new Vector3()).toArray()}];
      });
      const survey=(recorded[id]??[]).map(p=>{
        ray.set(new Vector3(p.x,5,-p.y),new Vector3(0,-1,0));const h=ray.intersectObjects(ground,true)[0];
        return {...p,currentTP:h?h.point.y+15:null,delta:h?h.point.y+15-p.tp:null,surface:h?.object.name??null};
      });
      assets[id]={...bounds(b.root),offset:b.root.position.y,scale:b.root.scale.toArray(),layers:b.layers,layerErrors:b.layerErrors,aabbCandidates:overlaps,recordedGround:survey,lowVertices:feet};
    }
    const walks = {};
    for (const [name,a] of Object.entries({west_front:[-30,18,-1,0,180],west_wall:[-28,32,-1,0,100],uc_front:[-65,16,-1,0,160],ekimae_wall:[-30,-25,-1,0,100],gate_passage:[-27,25,0,1,120],west_shop:[-56,18,0,1,60],uc_shop:[-82,15,0,1,80],ekimae_shop:[-34,-12,-1,-1,80],gate_clear:[-30,28,0,1,100]})) {
      const walk=window.__viewer.walkTest(...a);walk.inputs=a;
      if(walk.stoppedAt) {
        const [x,y,z]=walk.stoppedAt;const direction=new Vector3(a[2],0,-a[3]).normalize();const hits=[];
        for(const h of [.25,.5,1.3]) {
          ray.set(new Vector3(x,z+h,-y),direction);ray.far=.65;
          const hit=ray.intersectObjects(controls.obstacles,true)[0];
          if(hit){const names=[];for(let o=hit.object;o;o=o.parent)if(o.name)names.push(o.name);hits.push({height:h,distance:hit.distance,names});}
        }
        walk.blockers=hits;
        walk.nextGround=controls.groundAt(x+direction.x*.25,-y+direction.z*.25,z+.4);
      }
      walks[name]=walk;
    }
    return {coordinateOrder:'world X east, Y above T.P.15m, Z south; plan east,north,height',viewer:window.__viewer,assets,walks,status:document.querySelector('#status')?.textContent};
  },recorded);
  result.errors=errors;
  writeFileSync(`${out}/scene-fit.json`,JSON.stringify(result,null,2));
  assert.deepEqual(result.viewer.failed,[]);
  assert.deepEqual(errors,[]);
  for (const name of ['ground','street','exterior','terrain','context']) assert.equal(result.viewer[name].ok,true,name);
  for(const a of Object.values(result.assets)) {assert.deepEqual(a.layerErrors,[]);assert.deepEqual(a.scale,[1,1,1]);}
  for(const [walk,id] of [['west_shop','west-block'],['uc_shop','daiichi-kangin'],['ekimae_shop','ekimae']]) {
    assert.ok(result.walks[walk].blockers.some(h=>h.names.includes(id)),`${walk}: must stop at target building`);
  }
  assert.equal(result.walks.uc_front.path.length,160,'40m street walk');
  for (const [name, pose] of Object.entries({west_front:[-12,0,1.8,-49,35,16,60],uc_front:[-55,4,1.8,-81,33,24,60],ekimae_front:[-10,2,1.8,-50,-25,20,60],west_feet:[-25,15,2,-46,32,1,60],overview:[-5,-95,95,-58,18,12,58],center244:[-42,56,2,-68,76,14,55],west_base:[-56,18,2,-56,25,1.2,60],uc_base:[-82,16,2,-82,23,1,60]})) {
    if(process.env.VIEWS && !process.env.VIEWS.split(',').includes(name))continue;
    await page.evaluate(p=>{const f=window.__fit;f.controls.poseView(p.slice(0,3),p.slice(3,6),p[6],f.buildings[0].hints);},pose);
    await page.waitForTimeout(1500);
    await page.screenshot({path:`${out}/${name}.png`,timeout:400000});
    console.log(name,'captured');
  }
  // Temporary size trial only. These are not measured placement coordinates.
  if(!process.env.VIEWS || process.env.VIEWS.split(',').includes('props')) {
  result.propTrial = await page.evaluate(async () => {
    const { Box3, Vector3 } = await import('/node_modules/.vite/deps/three.js');
    const f=window.__fit;const rows=[];
    for(const [id,x,y] of [['hachiko_white_bollard',19,-28],['standing_notice_sign',21,-28],['grey_louvered_cabinet',23,-28]]) {
      const root=await f.io.loadGlb(`/assets/street/props/incoming/${id}/${id}.glb`);
      const ground=f.controls.groundAt(x,-y);if(ground===null)throw new Error(`No trial ground for ${id}`);
      const box=new Box3().setFromObject(root);const size=box.getSize(new Vector3()).toArray();
      root.position.set(x,ground-box.min.y,-y);root.name=`QA-only:${id}`;f.scene.add(root);
      rows.push({id,size,plan:[x,y,ground],placement:'temporary size trial, not a real-world placement'});
    }
    f.controls.poseView([21,-36,1.9],[21,-28,0.9],55,f.buildings[0].hints);
    const label=document.createElement('div');label.textContent='SIZE TRIAL ONLY — inferred dimensions; temporary positions (cabinet reference: Minami-Azabu)';
    Object.assign(label.style,{position:'fixed',top:'0',left:'0',right:'0',padding:'12px',background:'white',color:'black',font:'14px sans-serif',zIndex:'99999'});document.body.append(label);
    return rows;
  });
  await page.waitForTimeout(1500);
  await page.screenshot({path:`${out}/props-size-trial.png`,timeout:400000});
  }
  result.errors=errors;writeFileSync(`${out}/scene-fit.json`,JSON.stringify(result,null,2));
  assert.deepEqual(errors,[]);
  console.log('Full scene loaded; bounds, foot samples and walk paths saved. AABB candidates are not mesh intersections.');
} finally {await browser.close();}
