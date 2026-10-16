// Coarse projected aspect proxy, not a calibrated photograph or positional accuracy test.
import {NodeIO} from '@gltf-transform/core';
import {createHash} from 'node:crypto';
import {dirname} from 'node:path';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {Matrix4,Vector3,PerspectiveCamera} from 'three';
// These ratios describe historical handcrafted dog/plinth parts, not the current one-mesh scan.
// Legacy GLB coordinates already include the old world placement; do not apply the scan mount.
const legacyGlb='assets/street/hachiko/source/legacy/hachiko.glb';
const legacySha256='370db19f30af6c4c3ab9d49ae910fa99e14643fc507630f90655cf6d220d0ae5';
if(createHash('sha256').update(readFileSync(legacyGlb)).digest('hex')!==legacySha256) throw new Error('Historical Hachiko GLB does not match the preserved main asset');
function requiredMesh(root,name){
 const node=root.listNodes().find(n=>n.getName()===name);
 if(!node?.getMesh()) throw new Error('Historical comparison requires mesh '+name+' in its designated asset');
 return node;
}
const modelReference={scope:'historical_handcrafted_model_only',path:legacyGlb,sha256:legacySha256,placement:'world coordinates baked in legacy GLB; current scan placement is not applied',current_scan_evaluated:false};
const d=JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json'));
const camera=new PerspectiveCamera(44,750/900,.1,1000);camera.position.set(9.274,1.9,45.409);camera.lookAt(11.568,1.4,48.686);camera.updateMatrixWorld();
const root=(await new NodeIO().read(legacyGlb)).getRoot(),n=requiredMesh(root,'street_hachiko_plinth'),matrix=new Matrix4().fromArray(n.getWorldMatrix());
function bounds(sx,sy){const points=[];for(const p of n.getMesh().listPrimitives()){const a=p.getAttribute('POSITION');for(let i=0;i<a.getCount();i++){const q=new Vector3().fromArray(a.getElement(i,[]));q.x*=sx;q.y*=1;q.z*=sy;q.applyMatrix4(matrix).project(camera);points.push([(q.x+1)*750/2,(1-q.y)*900/2]);}}return[Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))];}
// glTF local X east, Y up, Z south, so depth scales local Z.
const photo=[635,1665,2050,3400],ratio=b=>(b[2]-b[0])/(b[3]-b[1]),after=bounds(1,1),initial=bounds(1.1/d.plinth_size_m[0],1/d.plinth_size_m[1]);
const report={model_reference:modelReference,reference:'july095.jpg, 3072x4096; manually read approximate whole stone block bounds, includes perspective side',photo_bounds_px:photo,photo_aspect:ratio(photo),initial_model_bounds_px:initial,initial_model_aspect:ratio(initial),final_model_bounds_px:after,final_model_aspect:ratio(after),relative_aspect_difference_initial:ratio(initial)/ratio(photo)-1,relative_aspect_difference_final:ratio(after)/ratio(photo)-1,caveat:'Model and photograph cameras are not calibrated to each other; perspective and manual edge readings affect this coarse silhouette proxy. Initial bounds reconstructed by scaling final block mesh; no positional, total sculpture or surface accuracy claim.'};
const output=process.argv[2]??'evidence/c2-hachiko/shape-check.json';mkdirSync(dirname(output),{recursive:true});
writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(report);
