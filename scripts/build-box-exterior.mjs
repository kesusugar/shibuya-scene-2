// BOX-2: independent dated layers. Never regenerate/reposition BOX-1 or its ground.
import {NodeIO} from '@gltf-transform/core';
import {Matrix4} from 'three';
import {readFileSync,writeFileSync,statSync,readdirSync} from 'node:fs';
import {join,relative} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const dir='assets/buildings/shibu-hachi-box',hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const baseHash='c1b262ee107e8b46baad917f30aff885420a8ac611f071b67469b542a18f7a5e';
assert.equal(hash(dir+'/web/shibu-hachi-box.glb'),baseHash,'Approved BOX-1 must remain byte-identical');
const config=JSON.parse(readFileSync(dir+'/source/exterior-signs/placement.json'));
const approved=JSON.parse(readFileSync(dir+'/source/placement-and-build.json'));
const basis=new Matrix4().makeRotationX(-Math.PI/2);
const world=basis.clone().multiply(new Matrix4().set(...approved.world_matrix_rows.flat())).multiply(basis.clone().invert());
const io=new NodeIO(),reports=[],layers={};
for(const item of config.components){
 assert.match(item.layer,/^signs_/,'Layer keys must match the shared :signs ancestor convention');
 assert(!Object.hasOwn(layers,item.layer),'Duplicate exterior sign layer');
 const source=dir+'/source/exterior-signs/'+item.input;
 assert.equal(hash(source),item.sha256,item.id+' input hash');
 const doc=await io.read(source),root=doc.getRoot();
 assert.equal(root.listAnimations().length,0,'Static displays only');
 // Reused architectural lettering was unlit frame material. The dated roof
 // identity is observed luminous; use the same illustrative pale factor as the icons.
 if(item.emissiveFactor)for(const material of root.listMaterials())material.setEmissiveFactor(item.emissiveFactor);
 const removedUV=[];
 if(item.removeUnusedUV){
  for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){
   const m=p.getMaterial(),uv=p.getAttribute('TEXCOORD_0');
   if(uv && !m.listExtensions().length && [m.getBaseColorTexture(),m.getMetallicRoughnessTexture(),m.getNormalTexture(),m.getOcclusionTexture(),m.getEmissiveTexture()].every(t=>!t)){
    p.setAttribute('TEXCOORD_0',null);removedUV.push(uv);
   }
  }
  const live=new Set(root.listMeshes().flatMap(m=>m.listPrimitives().flatMap(p=>p.listAttributes())));
  for(const uv of new Set(removedUV))if(!live.has(uv))uv.dispose();
 }
 const local=new Matrix4().makeTranslation(...item.positionGLTF).multiply(new Matrix4().makeRotationY((item.yawDegrees??0)*Math.PI/180)).multiply(new Matrix4().makeScale(...(item.scale??[1,1,1])));
 const transform=world.clone().multiply(local);
 for(const scene of root.listScenes()){
  const children=scene.listChildren(),parent=doc.createNode(item.id).setMatrix(transform.toArray());
  for(const node of children){scene.removeChild(node);parent.addChild(node);}
  scene.addChild(parent);
 }
 const output=dir+'/web/'+item.output;await io.write(output,doc);
 const triangles=root.listNodes().reduce((sum,n)=>sum+(n.getMesh()?.listPrimitives()??[]).reduce((s,p)=>s+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0);
 const primitives=root.listNodes().reduce((s,n)=>s+(n.getMesh()?.listPrimitives().length??0),0);
 reports.push({id:item.id,inputSha256:item.sha256,outputSha256:hash(output),triangles,primitives,bytes:statSync(output).size,removedUnusedUVAccessors:removedUV.length,bodyLocalMatrix:local.toArray(),worldMatrix:transform.toArray(),inverseWorldMatrix:transform.clone().invert().toArray()});
 layers[item.layer]=item.output;
}
const hintsPath=dir+'/web/viewer.json',hints=JSON.parse(readFileSync(hintsPath));
assert.equal(hints.groundElevationTP,15);
hints.layers=layers;writeFileSync(hintsPath,JSON.stringify(hints,null,2)+'\n');
const report={baseMain:'b4bd0a0',bodySha256:baseHash,bodyTransformUnchanged:true,groundAndSkirtUnchanged:true,staticClock:'2026-08-08 08:08:08',components:reports,totals:reports.reduce((s,r)=>({triangles:s.triangles+r.triangles,primitives:s.primitives+r.primitives,bytes:s.bytes+r.bytes}),{triangles:0,primitives:0,bytes:0})};
writeFileSync(dir+'/source/exterior-signs/build-report.json',JSON.stringify(report,null,2)+'\n');
const files={};function walk(path){for(const n of readdirSync(path,{withFileTypes:true})){const p=join(path,n.name);if(n.isDirectory())walk(p);else if(p.replaceAll('\\','/')!==dir+'/manifest.json')files[relative(dir,p).replaceAll('\\','/')]={bytes:statSync(p).size,sha256:hash(p)};}}walk(dir);
const manifest=JSON.parse(readFileSync(dir+'/manifest.json'));manifest.files=files;manifest.stats={triangles:14223+report.totals.triangles,primitives:14+report.totals.primitives,bytes:882780+report.totals.bytes};manifest.status='BOX-1 body retained; BOX-2 dated exterior displays; estimated installation';writeFileSync(dir+'/manifest.json',JSON.stringify(manifest,null,2)+'\n');
assert.equal(hash(dir+'/web/shibu-hachi-box.glb'),baseHash);
console.log(JSON.stringify(report,null,2));
