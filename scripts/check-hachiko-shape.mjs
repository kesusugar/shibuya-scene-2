// Coarse projected aspect proxy, not a calibrated photograph or positional accuracy test.
import {NodeIO} from '@gltf-transform/core';
import {readFileSync,writeFileSync} from 'node:fs';
import {Matrix4,Vector3,PerspectiveCamera} from 'three';
const d=JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json'));
const camera=new PerspectiveCamera(44,750/900,.1,1000);camera.position.set(9.274,1.9,45.409);camera.lookAt(11.568,1.4,48.686);camera.updateMatrixWorld();
const root=(await new NodeIO().read('assets/street/hachiko/web/hachiko.glb')).getRoot(),n=root.listNodes().find(n=>n.getName()==='street_hachiko_plinth'),matrix=new Matrix4().fromArray(n.getWorldMatrix());
function bounds(sx,sy){const points=[];for(const p of n.getMesh().listPrimitives()){const a=p.getAttribute('POSITION');for(let i=0;i<a.getCount();i++){const q=new Vector3().fromArray(a.getElement(i,[]));q.x*=sx;q.y*=1;q.z*=sy;q.applyMatrix4(matrix).project(camera);points.push([(q.x+1)*750/2,(1-q.y)*900/2]);}}return[Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))];}
// glTF local X east, Y up, Z south, so depth scales local Z.
const photo=[635,1665,2050,3400],ratio=b=>(b[2]-b[0])/(b[3]-b[1]),after=bounds(1,1),initial=bounds(1.1/d.plinth_size_m[0],1/d.plinth_size_m[1]);
const report={reference:'july095.jpg, 3072x4096; manually read approximate whole stone block bounds, includes perspective side',photo_bounds_px:photo,photo_aspect:ratio(photo),initial_model_bounds_px:initial,initial_model_aspect:ratio(initial),final_model_bounds_px:after,final_model_aspect:ratio(after),relative_aspect_difference_initial:ratio(initial)/ratio(photo)-1,relative_aspect_difference_final:ratio(after)/ratio(photo)-1,caveat:'Model and photograph cameras are not calibrated to each other; perspective and manual edge readings affect this coarse silhouette proxy. Initial bounds reconstructed by scaling final block mesh; no positional, total sculpture or surface accuracy claim.'};
writeFileSync('evidence/c2-hachiko/shape-check.json',JSON.stringify(report,null,2)+'\n');console.log(report);
