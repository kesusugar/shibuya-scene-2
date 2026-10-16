// Conservative solid-envelope interference check. Ground/paving contact is handled separately.
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,Box3,Triangle} from 'three';
import {readFileSync,writeFileSync,readdirSync} from 'node:fs';
const io=new NodeIO(),asset='assets/street/hachiko';
const placement=JSON.parse(readFileSync(asset+'/source/data/scan-placement.json'));
const inverse=new Matrix4().fromArray(placement.inverseMatrixColumnMajor);
const scan=(await io.read(asset+'/web/hachiko.glb')).getRoot(),box=new Box3();
for(const n of scan.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
 const a=p.getAttribute('POSITION');for(let i=0;i<a.getCount();i++)box.expandByPoint(new Vector3().fromArray(a.getElement(i,[])));
}
const results={};
const files={};
for(const id of ['hachiko-surround','tactile','props','core','plaza-facilities'])
 for(const f of readdirSync('assets/street/'+id+'/web').filter(f=>f.endsWith('.glb')))
  files[id+'/'+f]='assets/street/'+id+'/web/'+f;
for(const [id,file]of Object.entries(files)){
 try{
  const root=(await io.read(file)).getRoot();let checked=0,hits=0;const nodes={};
  for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
   const a=p.getAttribute('POSITION'),idx=p.getIndices(),matrix=inverse.clone().multiply(new Matrix4().fromArray(n.getWorldMatrix()));
   const pts=Array.from({length:a.getCount()},(_,i)=>new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(matrix));
   const nb=new Box3().setFromPoints(pts);if(!box.intersectsBox(nb))continue;
   for(let i=0;i<(idx?.getCount()??a.getCount());i+=3){
    const tri=new Triangle(...[0,1,2].map(j=>pts[idx?idx.getScalar(i+j):i+j]));checked++;
    if(box.intersectsTriangle(tri)){hits++;nodes[n.getName()]=(nodes[n.getName()]??0)+1;}
   }
  }
  results[id]={checkedTriangles:checked,envelopeIntersections:hits,nodes};
 }catch(e){results[id]={error:String(e)};}
}
const report={method:'Actual shipped triangles transformed into scan-local AABB. Zero intersections proves separation from entire scan envelope; nonzero needs closer review. Terrain/paving excluded as deliberate supporting surfaces.',bounds:{min:box.min.toArray(),max:box.max.toArray()},results};
writeFileSync('evidence/hachiko-scan-placement/surround-clearance.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
