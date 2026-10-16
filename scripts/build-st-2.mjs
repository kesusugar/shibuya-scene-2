// ST-2 shallow policebox exterior. Source geometry is local Y-up; apply the site transform once.
import {NodeIO} from '@gltf-transform/core';
import {Matrix3,Matrix4,Vector3} from 'three';
import {readFileSync,writeFileSync,readdirSync,statSync} from 'node:fs';
import {relative,join} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {buildST1Opening,cutWallPrimitive} from './build-st-1-opening.mjs';
const dir='assets/buildings/hachiko-policebox',source=dir+'/source/st-2';
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
export async function buildST2(){
 const c=JSON.parse(readFileSync(source+'/placement.json'));
 assert.equal(c.uniformScale,1,'Keep nominal proportions');assert(c.anchorAlongFace>0&&c.anchorAlongFace<1);
 assert([...c.anchorPlanEndpoints.flat(),c.groundY,c.frontOffset].every(Number.isFinite),'No unknown coordinate may default to zero');
 const opening=await buildST1Opening(c,{source:'assets/buildings/station-north/source/st-2',prefix:'st2'});
 const world=new Matrix4().fromArray(opening.worldMatrix),io=new NodeIO();
 const station='assets/buildings/station-north',shell=await io.read(station+'/web/station-north.glb'),hoarding=shell.getRoot().listNodes().find(n=>n.getName()==='stn_hoarding');
 const bounds=JSON.parse(readFileSync(station+'/source/st-2/opening.json'));
 const extra=cutWallPrimitive(hoarding.getMesh().listPrimitives()[0],hoarding,{...bounds,targetTriangles:[0,3],wallPlaneZ:.14},world);
 await io.write(station+'/web/station-north.glb',shell);
 opening.additionalCuts=[{targetNode:'stn_hoarding',targetPrimitive:0,cuts:extra.cuts}];opening.outputSha256=sha(station+'/web/station-north.glb');
 writeFileSync(station+'/source/st-2/build-report.json',JSON.stringify(opening,null,2)+'\n');
 const input=source+'/policebox_visible_facade_2025_v001.glb';assert.equal(sha(input),c.sourceSha256);
 const original=await io.read(input),components=[];
 for(const [layer,file] of Object.entries(c.parts)){
  const doc=await io.read(input),root=doc.getRoot(),buffer=root.listBuffers()[0],groups=new Map();
  for(const node of root.listNodes())for(const prim of node.getMesh()?.listPrimitives()??[]){
   const name=node.getName(),isSign=/^(50|51) \|/.test(name);
   if(c.omitted.includes(name)||(layer.startsWith('signs')!==isSign))continue;
   const material=prim.getMaterial(),key=material.getName(),g=groups.get(key)??{material,positions:[],normals:[],indices:[],nodes:[]};
   groups.set(key,g);g.nodes.push(name);
   const matrix=new Matrix4().fromArray(node.getWorldMatrix()),normalMatrix=new Matrix3().getNormalMatrix(matrix),pos=prim.getAttribute('POSITION'),norm=prim.getAttribute('NORMAL'),offset=g.positions.length/3;
   for(let i=0;i<pos.getCount();i++){
    g.positions.push(...new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(matrix).toArray());
    g.normals.push(...new Vector3().fromArray(norm.getElement(i,[])).applyMatrix3(normalMatrix).normalize().toArray());
   }
   for(const i of prim.getIndices().getArray())g.indices.push(i+offset);
  }
  // Remove old graph, keeping original materials. No authoring cameras or lights are exported.
  for(const scene of root.listScenes())scene.dispose();for(const n of root.listNodes())n.dispose();for(const m of root.listMeshes())m.dispose();
  const scene=doc.createScene(),parent=doc.createNode('ST2_site_transform').setMatrix(world.toArray());scene.addChild(parent);root.setDefaultScene(scene);
  for(const [key,g] of groups){
   if(key==='Upper visible aperture pane proxy')g.material.setName('st2_glass_upper_aperture_proxy');
   // Threshold is a facade component, not an interior floor or a change to terrain.
   if(key==='Provisional lower threshold')g.material.setName('st2_threshold_estimated');
   const mesh=doc.createMesh(key),p=doc.createPrimitive().setMaterial(g.material)
    .setAttribute('POSITION',doc.createAccessor(key+'_p',buffer).setType('VEC3').setArray(new Float32Array(g.positions)))
    .setAttribute('NORMAL',doc.createAccessor(key+'_n',buffer).setType('VEC3').setArray(new Float32Array(g.normals)))
    .setIndices(doc.createAccessor(key+'_i',buffer).setType('SCALAR').setArray(new Uint32Array(g.indices)));
   mesh.addPrimitive(p);parent.addChild(doc.createNode(key).setMesh(mesh));
  }
  // Dispose unused accessors/materials/buffers so only merged delivery geometry is serialized.
  const used=new Set(root.listMeshes().flatMap(m=>m.listPrimitives().flatMap(p=>[...p.listAttributes(),p.getIndices()])));
  for(const a of root.listAccessors())if(!used.has(a))a.dispose();
  const mats=new Set([...groups.values()].map(g=>g.material));for(const m of root.listMaterials())if(!mats.has(m))m.dispose();
  await io.write(dir+'/web/'+file,doc);
  components.push({layer,file,sha256:sha(dir+'/web/'+file),bytes:statSync(dir+'/web/'+file).size,primitives:groups.size,triangles:[...groups.values()].reduce((s,g)=>s+g.indices.length/3,0),nodes:[...groups.values()].flatMap(g=>g.nodes)});
 }
 const hints={groundElevationTP:15,planBounds:[44,-27,50,-19],layers:{'signs_2025-04-09':c.parts['signs_2025-04-09']}};
 writeFileSync(dir+'/web/viewer.json',JSON.stringify(hints,null,2)+'\n');
 for(const mode of ['day','night'])writeFileSync(dir+'/web/emissive_'+mode+'.json',JSON.stringify({'st2_glass_upper_aperture_proxy':{kind:'glass',emit:[0,0,0],estr:0}},null,2)+'\n');
 const report={main:'ecd30e7',worldMatrix:world.toArray(),components,omitted:c.omitted,openingReport:'../station-north/source/st-2/build-report.json',stats:{triangles:components.reduce((s,c)=>s+c.triangles,0),primitives:components.reduce((s,c)=>s+c.primitives,0),bytes:components.reduce((s,c)=>s+c.bytes,0)}};
 writeFileSync(source+'/build-report.json',JSON.stringify(report,null,2)+'\n');
 const files={};function walk(path){for(const e of readdirSync(path,{withFileTypes:true})){const p=join(path,e.name);if(e.isDirectory())walk(p);else if(e.name!=='manifest.json')files[relative(dir,p).replaceAll('\\','/')]={bytes:statSync(p).size,sha256:sha(p)};}}walk(dir);
 writeFileSync(dir+'/manifest.json',JSON.stringify({id:'hachiko-policebox',level:'B',sourceDate:c.date,status:'shallow visible facade; all metric dimensions and placement estimated; no interior',stats:report.stats,files},null,2)+'\n');
 return opening;
}
