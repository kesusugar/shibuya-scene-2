// Coarse height proxy: manually read photograph pixels vs world model heights, not calibrated accuracy.
import {NodeIO} from '@gltf-transform/core';
import {createHash} from 'node:crypto';
import {dirname} from 'node:path';
import {readFileSync,writeFileSync,statSync,mkdirSync} from 'node:fs';
import {Matrix4,Vector3} from 'three';
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
const d=JSON.parse(readFileSync('assets/street/hachiko-surround/source/data/layout.json'));
const io=new NodeIO(),s=(await io.read('assets/street/hachiko-surround/source/legacy/hachiko-surround-pr88.glb')).getRoot(),h=(await io.read(legacyGlb)).getRoot();
function range(root,name){const n=requiredMesh(root,name),ys=[];for(const p of n.getMesh().listPrimitives()){const a=p.getAttribute('POSITION'),m=new Matrix4().fromArray(n.getWorldMatrix());for(let i=0;i<a.getCount();i++)ys.push(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m).y)}return[Math.min(...ys),Math.max(...ys)];}
const needles=range(s,'street_surround_needle'),rails=range(s,'street_surround_silver'),dog=range(h,'street_hachiko_dog'),height=dog[1]-dog[0];
const photo={source:'july095.jpg / 3072x4096',approximate_y_px:{shrub_top:915,rear_rail_top:2012,dog_top:83,dog_paw_bottom:1432}};
const report={model_reference:modelReference,surround_asset:'assets/street/hachiko-surround/source/legacy/hachiko-surround-pr88.glb',surround_sha256:createHash('sha256').update(readFileSync('assets/street/hachiko-surround/source/legacy/hachiko-surround-pr88.glb')).digest('hex'),photo,photo_gap_over_dog_height:(2012-915)/(1432-83),model_world_ranges_m:{needles,rails,dog},final_world_gap_over_dog_height:(needles[1]-rails[1])/height,initial_nominal_gap_over_dog_height:(d.wall_height_m-.03+.67-d.rail_rear_height_m)/height,final_nominal_gap_over_dog_height:(d.wall_height_m-.03+d.shrub_height_m-d.rail_rear_height_m)/height,caveat:'Photograph pixel ratio and model world ratio are different measures. Uncalibrated perspective, occlusion, manually read approximate points and ground slope apply. Directional silhouette proxy only, not positional/physical accuracy or a pass score.'};
const output=process.argv[2]??'evidence/c2-hachiko-surround/shape-check.json';mkdirSync(dirname(output),{recursive:true});
writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(report);
const primitives=s.listNodes().flatMap(n=>n.getMesh()?.listPrimitives()??[]);console.log({triangles:primitives.reduce((t,p)=>t+p.getIndices().getCount()/3,0),primitives:primitives.length,bytes:statSync('assets/street/hachiko-surround/source/legacy/hachiko-surround-pr88.glb').size});
