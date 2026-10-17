import {NodeIO} from '@gltf-transform/core';
import {readFileSync,writeFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
const io=new NodeIO();
const fingerprint=p=>{const b=readFileSync(p);return {bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
for(const id of ['box-contents','hachiko-surround']){
 const base=`assets/street/${id}/`,manifest=JSON.parse(readFileSync(base+'manifest.json'));
 const outputs={},total={bytes:0,triangles:0,primitives:0};
 for(const f of readdirSync(base+'web').sort()){
  const data=fingerprint(base+'web/'+f);outputs['web/'+f]=data;
  if(!f.endsWith('.glb'))continue;
  const root=(await io.read(base+'web/'+f)).getRoot(),ps=root.listMeshes().flatMap(m=>m.listPrimitives());
  data.triangles=ps.reduce((n,p)=>n+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0);
  data.primitives=ps.length;
  for(const k of Object.keys(total))total[k]+=data[k];
 }
 manifest.outputs=outputs;manifest.total=total;
 if(id==='hachiko-surround'){
  manifest.status='Authored v002 shrubs and seating installed; equipment frame retained; candidate curves/paving not installed';
  manifest.build_stats.triangles=total.triangles;
  for(const [path,info] of Object.entries(manifest.files))manifest.files[path]={...info,...fingerprint(base+path)};
 }
 writeFileSync(base+'manifest.json',JSON.stringify(manifest,null,2)+'\n');console.log(id,total);
}
const base='assets/street/hachiko/',manifest=JSON.parse(readFileSync(base+'manifest.json'));
const p=JSON.parse(readFileSync(base+'source/data/scan-placement.json'));
manifest.status='Complete original scan; station-facing yaw estimated from fixed landmarks/plaque, ground remeasured at 371 rim points';
manifest.build_stats.anchor_tp=p.anchorTP;manifest.build_stats.max_burial_m=p.ground.maxBurialM;
for(const path of Object.keys(manifest.files))manifest.files[path]=fingerprint(base+path);
writeFileSync(base+'manifest.json',JSON.stringify(manifest,null,2)+'\n');
