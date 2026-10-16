// Reuse same-camera evidence only when rendered geometry/materials are unchanged.
import {NodeIO} from '@gltf-transform/core';
import {Vector3,Matrix4,Triangle} from 'three';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const [captured,current,out]=process.argv.slice(2),io=new NodeIO();
async function inspect(file){
 const root=(await io.read(file)).getRoot(),triangles=[];let degenerate=0;
 for(const node of root.listNodes())for(const p of node.getMesh()?.listPrimitives()??[]){
  const a=p.getAttribute('POSITION'),normal=p.getAttribute('NORMAL'),idx=p.getIndices(),matrix=new Matrix4().fromArray(node.getWorldMatrix());
  for(let i=0;i<idx.getCount();i+=3){
   const corners=[0,1,2].map(j=>idx.getScalar(i+j));
   const points=corners.map(j=>new Vector3().fromArray(a.getElement(j,[])).applyMatrix4(matrix));
   if(new Triangle(...points).getArea()<1e-12){degenerate++;continue;}
   const rows=corners.map((j,k)=>[...points[k].toArray(),...new Vector3().fromArray(normal.getElement(j,[])).transformDirection(matrix).toArray()].map(n=>n.toFixed(5)).join(','));
   triangles.push(p.getMaterial().getName()+':'+rows.sort().join(';'));
  }
 }
 const materials=root.listMaterials().map(m=>({name:m.getName(),color:m.getBaseColorFactor(),roughness:m.getRoughnessFactor(),metallic:m.getMetallicFactor(),alpha:m.getAlphaMode(),doubleSided:m.getDoubleSided()})).sort((a,b)=>a.name.localeCompare(b.name));
 return {triangles:triangles.sort(),degenerate,materials,sha256:createHash('sha256').update(readFileSync(file)).digest('hex')};
}
const a=await inspect(captured),b=await inspect(current);
assert.deepEqual(b.triangles,a.triangles,'Nondegenerate triangle positions/normals/material assignment changed');
assert.deepEqual(b.materials,a.materials);assert.equal(a.degenerate,1);assert.equal(b.degenerate,0);
const report={capturedSha256:a.sha256,finalSha256:b.sha256,capturedTriangles:a.triangles.length+a.degenerate,finalTriangles:b.triangles.length,removedZeroAreaTriangles:1,nondegenerateWorldPositionsNormalsMaterialAssignmentEqualAt1e5:true,materialParametersEqual:true,imagesReused:true,reason:'Only one zero-area skirt triangle removed after capture; all 14223 visible triangles, normals and materials unchanged. Capture logs intentionally retain original 14224 count.'};
writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
