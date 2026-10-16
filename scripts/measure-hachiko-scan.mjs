import {NodeIO} from '@gltf-transform/core';
import {BufferGeometry,BufferAttribute,Matrix4,Mesh,MeshBasicMaterial,DoubleSide,Raycaster,Vector3} from 'three';
import {readFileSync,writeFileSync} from 'node:fs';
const [file,out]=process.argv.slice(2),io=new NodeIO();
const layout=JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json'));
const rotation=new Matrix4().makeRotationY(layout.yaw_deg*Math.PI/180),surfaces=[];
for(const n of (await io.read('assets/ground/core/web/ground_core.glb')).getRoot().listNodes()){
 if(!n.getName().startsWith('ground_sidewalk'))continue;
 for(const p of n.getMesh()?.listPrimitives()??[]){
  const g=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION').getArray(),3));
  g.setIndex(new BufferAttribute(p.getIndices().getArray(),1));g.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
  const m=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));m.updateMatrixWorld();surfaces.push(m);
 }
}
const positions=[],welded=new Map(),edges=new Map();
for(const n of (await io.read(file)).getRoot().listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
 const a=p.getAttribute('POSITION'),ids=[];
 for(let i=0;i<a.getCount();i++){
  const v=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix())),key=v.toArray().join(',');
  if(!welded.has(key)){welded.set(key,positions.length);positions.push(v);}ids.push(welded.get(key));
 }
 const idx=p.getIndices().getArray();
 for(let i=0;i<idx.length;i+=3)for(let j=0;j<3;j++){
  const a=ids[idx[i+j]],b=ids[idx[i+(j+1)%3]],key=[Math.min(a,b),Math.max(a,b)].join(',');
  edges.set(key,(edges.get(key)??0)+1);
 }
}
const rim=[...edges].filter(([key,count])=>count===1&&key.split(',').every(i=>positions[+i].y<.1));
if(rim.length!==371)throw Error('Unexpected lower boundary '+rim.length);
const ray=new Raycaster(),samples=[];
for(const id of new Set(rim.flatMap(([key])=>key.split(',').map(Number)))){
 const local=positions[id],w=local.clone().applyMatrix4(rotation);w.x+=layout.xy[0];w.z-=layout.xy[1];
 ray.set(new Vector3(w.x,50,w.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(surfaces,false)[0];
 if(!hit)throw Error('Rim outside sidewalk');
 samples.push({local:local.toArray(),worldXZ:[w.x,w.z],groundY:hit.point.y});
}
const anchor=Math.min(...samples.map(s=>s.groundY-s.local[1]))-.001;
const matrix=new Matrix4().makeTranslation(layout.xy[0],anchor,-layout.xy[1]).multiply(rotation);
const gaps=samples.map(s=>s.local[1]+anchor-s.groundY);
const result={basisCommit:'e1124dd1b5412d1cd4140d4272ebaf86ea7ca79e',position:[layout.xy[0],anchor,-layout.xy[1]],yawDegrees:layout.yaw_deg,scale:[1,1,1],datumTP:15,anchorTP:anchor+15,matrixColumnMajor:matrix.toArray(),inverseMatrixColumnMajor:matrix.clone().invert().toArray(),ground:{samples:samples.length,lowerBoundaryEdges:rim.length,maxGapM:Math.max(...gaps),maxBurialM:-Math.min(...gaps),samplesDetail:samples},note:'Rigid translation/yaw only. Lowest upper rim discrepancy is buried 1mm; real dimensions and ground fit remain estimates.'};
writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({...result,ground:{...result.ground,samplesDetail:undefined}},null,2));
