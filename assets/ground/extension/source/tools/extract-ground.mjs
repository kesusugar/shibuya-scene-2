import {NodeIO} from '@gltf-transform/core';
import {writeFileSync} from 'node:fs';
import {Matrix4,Vector3} from 'three';
const root=(await new NodeIO().read(process.argv[2])).getRoot(),tri=[];
for(const n of root.listNodes())if(/^ground_(road|intersection|sidewalk|fill)/.test(n.getName()))for(const p of n.getMesh()?.listPrimitives()??[]) {
 const pos=p.getAttribute('POSITION'),idx=p.getIndices(),m=new Matrix4().fromArray(n.getWorldMatrix());
 for(let i=0;i<idx.getCount();i+=3){const t=[];for(let j=0;j<3;j++){const v=new Vector3().fromArray(pos.getElement(idx.getScalar(i+j),[])).applyMatrix4(m);t.push([v.x,-v.z,v.y+15]);}tri.push(t);}
}writeFileSync(process.argv[3],JSON.stringify(tri));console.log(tri.length);
