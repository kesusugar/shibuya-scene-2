// Actual shipped geometry and measured Core ground; no scene or walking changes.
import {NodeIO} from '@gltf-transform/core';
import {Box3,Triangle,Vector3,Matrix4,Raycaster,BufferGeometry,BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide} from 'three';
import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const dir='assets/buildings/shibu-hachi-box', io=new NodeIO();
const placement=JSON.parse(readFileSync(dir+'/source/placement-and-build.json'));
const basis=new Matrix4().makeRotationX(-Math.PI/2);
const world=basis.clone().multiply(new Matrix4().set(...placement.world_matrix_rows.flat())).multiply(basis.clone().invert());
const inverse=world.clone().invert(),surfaces=[];
for(const n of (await io.read('assets/ground/core/web/ground_core.glb')).getRoot().listNodes()) {
 if(!n.getName().startsWith('ground_sidewalk')&&!n.getName().startsWith('ground_fill'))continue;
 for(const p of n.getMesh()?.listPrimitives()??[]){
  const g=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION').getArray(),3));
  g.setIndex(new BufferAttribute(p.getIndices().getArray(),1));g.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
  const m=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));m.updateMatrixWorld();surfaces.push(m);
 }
}
const ray=new Raycaster(),deck=[];
for(let i=0;i<=48;i++){
 const x=-5.953958414148326+(5.744397750235235+5.953958414148326)*i/48;
 const high=.248, knee=2.0098772048950195, end=5.744397750235235;
 const y=x<=knee?high:high-(high+.081863014)*(x-knee)/(end-knee);
 const p=new Vector3(x,y,1.766).applyMatrix4(world);
 ray.set(new Vector3(p.x,40,p.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(surfaces,false)[0];
 assert(hit,'Missing ground is not zero');deck.push({bodyX:x,world:p.toArray(),groundY:hit.point.y,deckAboveGroundM:p.y-hit.point.y});
}
assert(Math.min(...deck.map(p=>p.deckAboveGroundM))>=.003,'Terrace walking surface buried');
const envelope=new Box3(new Vector3(-6.42,-.1644,-1.84),new Vector3(6.42,2.81,1.84));
const checks={};
for(const [id,file]of Object.entries({
 'A8/plaza-kiosk':'assets/buildings/plaza-kiosk/web/plaza-kiosk.glb',
 'station-service':'assets/buildings/station-service/web/station-service.glb',
 'station-concourse':'assets/buildings/station-concourse/web/station-concourse.glb',
 'station-west-viaduct':'assets/buildings/station-west-viaduct/web/station-west-viaduct.glb',
 'hachiko':'assets/street/hachiko/web/hachiko.glb',
 'hachiko-surround':'assets/street/hachiko-surround/web/hachiko-surround.glb',
 'plaza-facilities':'assets/street/plaza-facilities/web/plaza-facilities.glb',
 'street-core':'assets/street/core/web/street_core.glb',
})){
 let hits=0,triangles=0;
 for(const n of (await io.read(file)).getRoot().listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const a=p.getAttribute('POSITION'),idx=p.getIndices(),matrix=inverse.clone().multiply(new Matrix4().fromArray(n.getWorldMatrix()));
  const points=Array.from({length:a.getCount()},(_,i)=>new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(matrix));
  if(!envelope.intersectsBox(new Box3().setFromPoints(points)))continue;
  for(let i=0;i<(idx?.getCount()??a.getCount());i+=3){triangles++;if(envelope.intersectsTriangle(new Triangle(...[0,1,2].map(j=>points[idx?idx.getScalar(i+j):i+j]))))hits++;}
 }
 checks[id]={testedTriangles:triangles,envelopeIntersections:hits};assert.equal(hits,0,id+' intersects BOX envelope');
}
const report={method:'Core ground raycasts at 49 terrace-front samples; conservative whole BOX local envelope vs actual shipped neighbouring triangles. Supporting pavement excluded from interference. No FPS claim.',deckMinGapM:Math.min(...deck.map(p=>p.deckAboveGroundM)),deckMaxRiseM:Math.max(...deck.map(p=>p.deckAboveGroundM)),deckSamples:deck,neighbours:checks,entry:'Retained rear strip 226mm, level finish step18mm; inherited rear upstand up to312mm on descending run. No new walk surfaces, accessible entrance or indoor navigation claimed.'};
writeFileSync('evidence/box-1/geometry-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,deckSamples:undefined},null,2));
