// ST-1: two shallow surfaces in the existing JR asset. No structural rebuild.
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,Ray} from 'three';
import {readFileSync,writeFileSync,readdirSync,statSync} from 'node:fs';
import {join,relative} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const dir='assets/buildings/station-north',source=dir+'/source/st-1';
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const c=JSON.parse(readFileSync(source+'/placement.json'));
const bodyHash=hash(dir+'/web/station-north.glb');
assert.equal(bodyHash,'eb1b9607fa28c0410ada219fd42cbb6f19592ddb2bb6002050869eb5bf65ed09','Preserve the approved station structure');
const [a,b]=c.anchorPlanEndpoints,t=new Vector3(b[0]-a[0],0,-(b[1]-a[1])).normalize();
const n=new Vector3(-t.z,0,t.x),yaw=Math.atan2(n.x,n.z);
const anchor=new Vector3(a[0]+(b[0]-a[0])*c.anchorAlongFace,c.groundY,-a[1]-(b[1]-a[1])*c.anchorAlongFace).addScaledVector(n,c.frontOffset);
assert(c.uniformScale>0 && c.uniformScale<2);
assert(c.groundY+4.2*c.uniformScale<c.soffitY);
const world=new Matrix4().makeTranslation(...anchor.toArray()).multiply(new Matrix4().makeRotationY(yaw)).multiply(new Matrix4().makeScale(c.uniformScale,c.uniformScale,c.uniformScale));
const io=new NodeIO(),layers={},reports=[],signMaterials=new Map();
// Use the visible replacement terrain, never the removed provisional Core fill.
const ground=[];
for(const id of ['core','extension','exterior-east','exterior-middle','exterior-west'])for(const file of readdirSync('assets/ground/'+id+'/web').filter(f=>f.endsWith('.glb'))){
 const root=(await io.read('assets/ground/'+id+'/web/'+file)).getRoot();
 for(const node of root.listNodes()){
  if(node.getName()==='ground_fill')continue;
  const matrix=new Matrix4().fromArray(node.getWorldMatrix());
  for(const p of node.getMesh()?.listPrimitives()??[]){
   const pos=p.getAttribute('POSITION'),idx=p.getIndices();
   for(let i=0;i<(idx?.getCount()??pos.getCount());i+=3)ground.push([0,1,2].map(k=>new Vector3().fromArray(pos.getElement(idx?idx.getScalar(i+k):i+k,[])).applyMatrix4(matrix)));
  }
 }
}
function groundAt(point){
 const ray=new Ray(new Vector3(point.x,50,point.z),new Vector3(0,-1,0));let y=-Infinity;
 for(const tri of ground){const hit=ray.intersectTriangle(...tri,false,new Vector3());if(hit)y=Math.max(y,hit.y);}
 assert(Number.isFinite(y),'Missing visible ground; do not assume zero');return y;
}
for(const item of c.components){
 assert.equal(hash(source+'/'+item.input),item.sha256);
 assert.equal(item.layer.startsWith('signs_'),item.id==='entry-fascia');
 const doc=await io.read(source+'/'+item.input),root=doc.getRoot();
 // applyLook visits mesh materials. Keep this imported fascia's materials
 // independent so non-default nightSign is applied once, not once per reuse.
 if(item.id==='entry-fascia'){
  const original=root.listMaterials();
  original.forEach(m=>signMaterials.set(m.getName(),{kind:'sign',emit:m.getEmissiveFactor(),estr:1}));
  for(const p of root.listMeshes().flatMap(m=>m.listPrimitives()))p.setMaterial(p.getMaterial().clone());
  original.forEach(m=>m.dispose());
 }
 const matrix=world.clone().multiply(new Matrix4().makeTranslation(...item.position));
 const bottomFits=[];
 if(item.id==='centre-pier-cladding' && c.fitPierBottomToVisibleGround){
  for(const node of root.listNodes())for(const p of node.getMesh()?.listPrimitives()??[]){
   const pos=p.getAttribute('POSITION'),transform=matrix.clone().multiply(new Matrix4().fromArray(node.getWorldMatrix())),inverse=transform.clone().invert();
   for(let i=0;i<pos.getCount();i++){
    const local=pos.getElement(i,[]);if(Math.abs(local[1])>1e-6)continue;
    const point=new Vector3().fromArray(local).applyMatrix4(transform),oldY=point.y;
    point.y=groundAt(point)-.005;
    bottomFits.push({worldXZ:[point.x,point.z],oldY,newY:point.y,groundY:point.y+.005});
    pos.setElement(i,point.applyMatrix4(inverse).toArray());
   }
  }
 }
 for(const scene of root.listScenes()){
  const children=scene.listChildren(),parent=doc.createNode('ST1_'+item.id).setMatrix(matrix.toArray());
  children.forEach(n=>{scene.removeChild(n);parent.addChild(n);});scene.addChild(parent);
 }
 await io.write(dir+'/web/'+item.output,doc);layers[item.layer]=item.output;
 const primitives=root.listNodes().flatMap(n=>n.getMesh()?.listPrimitives()??[]);
 reports.push({id:item.id,layer:item.layer,output:item.output,sha256:hash(dir+'/web/'+item.output),bytes:statSync(dir+'/web/'+item.output).size,triangles:primitives.reduce((s,p)=>s+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),primitives:primitives.length,worldMatrix:matrix.toArray(),bottomFits});
}
const hints=JSON.parse(readFileSync(dir+'/web/viewer.json'));hints.layers=layers;
assert.equal(hints.groundElevationTP,15);writeFileSync(dir+'/web/viewer.json',JSON.stringify(hints,null,2)+'\n');
for(const mode of ['day','night']){
 const path=dir+'/web/emissive_'+mode+'.json',table=JSON.parse(readFileSync(path));
 for(const [name,row] of signMaterials)table[name]=row;
 writeFileSync(path,JSON.stringify(table,null,2)+'\n');
}
const report={main:c.main,bodySha256:bodyHash,bodyUnchanged:true,anchorWorld:anchor.toArray(),uniformScale:c.uniformScale,yawDegrees:yaw*180/Math.PI,components:reports};
writeFileSync(source+'/build-report.json',JSON.stringify(report,null,2)+'\n');
const manifest=JSON.parse(readFileSync(dir+'/manifest.json')),files={};
function walk(path){for(const ent of readdirSync(path,{withFileTypes:true})){const p=join(path,ent.name);if(ent.isDirectory())walk(p);else if(p.replaceAll('\\','/')!==dir+'/manifest.json')files[relative(dir,p).replaceAll('\\','/')]={bytes:statSync(p).size,sha256:hash(p)};}}
walk(dir);manifest.files=files;
manifest.st1={status:'estimated shallow exterior fit; dated fascia and wall cladding only',...report};
const stats={triangles:0,primitives:0,bytes:0};
for(const name of readdirSync(dir+'/web').filter(f=>f.endsWith('.glb'))){
 stats.bytes+=statSync(dir+'/web/'+name).size;
 const root=(await io.read(dir+'/web/'+name)).getRoot();
 for(const p of root.listNodes().flatMap(n=>n.getMesh()?.listPrimitives()??[])){
  stats.primitives++;stats.triangles+=(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3;
 }
}
manifest.stats=stats;
writeFileSync(dir+'/manifest.json',JSON.stringify(manifest,null,2)+'\n');
assert.equal(hash(dir+'/web/station-north.glb'),bodyHash);
console.log(JSON.stringify(report,null,2));
