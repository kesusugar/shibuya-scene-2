// node export_triangles.mjs before.glb after.glb output-directory
import { NodeIO } from '@gltf-transform/core';
import { Vector3, Matrix4 } from 'three';
import { writeFileSync, mkdirSync } from 'node:fs';
const [before,after,directory]=process.argv.slice(2);
mkdirSync(directory,{recursive:true});
for (const [name,file] of [['before',before],['after',after]]) {
  const root=(await new NodeIO().read(file)).getRoot(),out={};
  for (const n of root.listNodes()) {
    const triangles=[],matrix=new Matrix4().fromArray(n.getWorldMatrix());
    for (const p of n.getMesh()?.listPrimitives()??[]) {
      const pos=p.getAttribute('POSITION'),idx=p.getIndices();
      for (let i=0;i<idx.getCount();i+=3) triangles.push([0,1,2].map(j=>new Vector3().fromArray(pos.getElement(idx.getScalar(i+j),[])).applyMatrix4(matrix)).map(v=>[v.x,-v.z,v.y]));
    }
    if (triangles.length)out[n.getName()]=triangles;
  }
  writeFileSync(`${directory}/${name}-triangles.json`,JSON.stringify(out));
}
