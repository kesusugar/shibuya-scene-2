// Derive the visible station shell from the preserved PR81 GLB. No runtime or walking changes.
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3} from 'three';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const dir='assets/buildings/station-north',source=dir+'/source/st-1-opening';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const area=poly=>Math.abs(poly.reduce((s,v,i)=>{const w=poly[(i+1)%poly.length];return s+v.p.x*w.p.y-w.p.x*v.p.y;},0))/2;
function clip(poly,axis,bound,positive){
 const out=[],distance=v=>(positive?1:-1)*(v.p[axis]-bound);
 for(let i=0;i<poly.length;i++){
  const a=poly[i],b=poly[(i+1)%poly.length],da=distance(a),db=distance(b),insideA=da>=0,insideB=db>=0;
  if(insideA)out.push(a);
  if(insideA!==insideB){const t=da/(da-db);out.push({p:a.p.clone().lerp(b.p,t),weights:a.weights.map((v,k)=>v+(b.weights[k]-v)*t)});}
 }
 return out;
}
function subtract(poly,c){
 const outside=[];let inside=poly;
 for(const [axis,bound,positive] of [['x',c.xMin,true],['x',c.xMax,false],['y',c.bottomY,true],['y',c.topY,false]]){
  if(!inside.length)break;
  const fragment=clip(inside,axis,bound,!positive);
  if(fragment.length>=3 && area(fragment)>1e-10)outside.push(fragment);
  inside=clip(inside,axis,bound,positive);
 }
 return {outside,removedArea:inside.length>=3?area(inside):0};
}
export async function buildST1Opening(placement,options={}){
 const source=options.source??dir+'/source/st-1-opening',prefix=options.prefix??'st1';
 const c=JSON.parse(readFileSync(source+'/opening.json'));
 if(!options.source){
 const fascia=placement.components.find(c=>c.id==='entry-fascia');
 assert(c.xMin>=fascia.position[0]-2.4-1e-6 && c.xMax<=fascia.position[0]+2.4+1e-6,'Opening must remain under the selected fascia');
 assert(Math.abs(c.topY+c.topClearanceToFascia-fascia.position[1])<1e-8);
 assert(c.depth>0 && c.depth<=1 && c.bottomY>=-1,'Shallow exterior only');
 }
 const bytes=readFileSync(source+'/'+c.baseline);assert.equal(sha(bytes),c.baselineSha256);
 const [a,b]=placement.anchorPlanEndpoints,t=new Vector3(b[0]-a[0],0,-(b[1]-a[1])).normalize(),n=new Vector3(-t.z,0,t.x);
 const anchor=new Vector3(a[0]+(b[0]-a[0])*placement.anchorAlongFace,placement.groundY,-a[1]-(b[1]-a[1])*placement.anchorAlongFace).addScaledVector(n,placement.frontOffset);
 const world=new Matrix4().makeTranslation(...anchor.toArray()).multiply(new Matrix4().makeRotationY(Math.atan2(n.x,n.z))).multiply(new Matrix4().makeScale(placement.uniformScale,placement.uniformScale,placement.uniformScale));
 const io=new NodeIO(),doc=await io.readBinary(bytes),root=doc.getRoot(),target=root.listNodes().filter(n=>n.getName()===c.targetNode);
 assert.equal(target.length,1);const node=target[0],prim=node.getMesh().listPrimitives()[c.targetPrimitive];
 const {position,originalIndices,result,cuts,appended}=cutWallPrimitive(prim,node,c,world);
 const buffer=position.getBuffer(),jambMaterial=doc.createMaterial(prefix+'_entry_recess_wall').setBaseColorFactor([.32,.34,.32,1]).setRoughnessFactor(.9).setDoubleSided(true);
 const backMaterial=doc.createMaterial(prefix+'_entry_recess_back').setBaseColorFactor([.035,.04,.035,1]).setRoughnessFactor(1).setDoubleSided(true);
 const mesh=doc.createMesh(prefix.toUpperCase()+'_shallow_entry_recess');
 const z=c.wallPlaneZ,back=z-c.depth,x0=c.xMin,x1=c.xMax,y0=c.bottomY,y1=c.topY;
 const quads=[
  [[x0,y0,z],[x0,y0,back],[x0,y1,back],[x0,y1,z]],
  [[x1,y0,back],[x1,y0,z],[x1,y1,z],[x1,y1,back]],
  [[x0,y1,z],[x0,y1,back],[x1,y1,back],[x1,y1,z]],
  [[x0,y0,back],[x1,y0,back],[x1,y1,back],[x0,y1,back]],
 ];
 for(const [name,faces,material] of [['reveals',quads.slice(0,3),jambMaterial],['back',[quads[3]],backMaterial]]){
  const positions=[],normals=[],idx=[];
  for(const q of faces){
   const start=positions.length/3,v=q.map(p=>new Vector3(...p)),normal=v[1].clone().sub(v[0]).cross(v[2].clone().sub(v[0])).normalize();
   q.forEach(p=>{positions.push(...p);normals.push(...normal.toArray());});idx.push(start,start+1,start+2,start,start+2,start+3);
  }
  const p=doc.createPrimitive().setAttribute('POSITION',doc.createAccessor(name+'_position',buffer).setType('VEC3').setArray(new Float32Array(positions))).setAttribute('NORMAL',doc.createAccessor(name+'_normal',buffer).setType('VEC3').setArray(new Float32Array(normals))).setIndices(doc.createAccessor(name+'_indices',buffer).setType('SCALAR').setArray(new Uint16Array(idx))).setMaterial(material);
  mesh.addPrimitive(p);
 }
 const reveal=doc.createNode(prefix.toUpperCase()+'_shallow_entry_recess').setMesh(mesh).setMatrix(world.toArray());root.listScenes()[0].addChild(reveal);
 const out=dir+'/web/station-north.glb';await io.write(out,doc);
 const report={main:c.main,baseline:c.baseline,baselineSha256:c.baselineSha256,outputSha256:sha(readFileSync(out)),targetNode:c.targetNode,targetPrimitive:c.targetPrimitive,originalTriangles:originalIndices.length/3,outputTriangles:result.length/3,originalVertexCount:position.getCount()-appended,appendedVertices:appended,cuts,removedArea:cuts.reduce((s,c)=>s+c.removedArea,0),depth:c.depth,worldMatrix:world.toArray(),addedTriangles:8,addedPrimitives:2,noFloorOrWalkSurfaceAdded:true,collisionCodeUnchanged:true,walkableEntrance:false,reference:c.reference};
 writeFileSync(source+'/build-report.json',JSON.stringify(report,null,2)+'\n');return report;
}

// Shared bounded clipper: preserves original attributes and all unselected triangles.
export function cutWallPrimitive(prim,node,c,world){
 const position=prim.getAttribute('POSITION'),indices=prim.getIndices(),originalIndices=Array.from(indices.getArray());
 assert.deepEqual([...prim.listSemantics()].sort(),['NORMAL','POSITION']);
 const toLocal=world.clone().invert().multiply(new Matrix4().fromArray(node.getWorldMatrix()));
 const attrs=Object.fromEntries(prim.listSemantics().map(name=>[name,{accessor:prim.getAttribute(name),values:Array.from(prim.getAttribute(name).getArray())}]));
 const result=[],cuts=[];let appended=0;
 for(let i=0;i<originalIndices.length;i+=3){
  const ids=originalIndices.slice(i,i+3),poly=ids.map((id,j)=>({p:new Vector3().fromArray(position.getElement(id,[])).applyMatrix4(toLocal),weights:[0,0,0].map((_,k)=>j===k?1:0)}));
  const onPlane=poly.every(v=>Math.abs(v.p.z-c.wallPlaneZ)<c.planeTolerance);
  const overlap=onPlane?subtract(poly,c):{removedArea:0};
  if(overlap.removedArea<1e-8){result.push(...ids);continue;}
  assert(c.targetTriangles.includes(i/3),'Refuse to cut an unapproved triangle');
  cuts.push({triangle:i/3,originalIndices:ids,removedArea:overlap.removedArea});
  for(const fragment of overlap.outside){
   const start=position.getCount()+appended;
   for(const v of fragment){
    for(const {accessor,values} of Object.values(attrs)){
     const sourceValues=ids.map(id=>accessor.getElement(id,[]));
     for(let k=0;k<accessor.getElementSize();k++)values.push(sourceValues.reduce((s,row,j)=>s+row[k]*v.weights[j],0));
    }
    appended++;
   }
   for(let j=1;j<fragment.length-1;j++){
    if(area([fragment[0],fragment[j],fragment[j+1]])>1e-10)result.push(start,start+j,start+j+1);
   }
  }
 }
 assert.deepEqual(cuts.map(r=>r.triangle).sort((a,b)=>a-b),c.targetTriangles);
 for(const {accessor,values} of Object.values(attrs))accessor.setArray(new Float32Array(values));
 indices.setArray(new Uint16Array(result));assert(position.getCount()<65536);
 return {position,originalIndices,result,cuts,appended};
}
