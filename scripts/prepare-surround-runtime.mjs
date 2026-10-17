import {NodeIO} from '@gltf-transform/core';
import {writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
const base='assets/street/hachiko-surround/',io=new NodeIO();
const doc=await io.read(base+'source/legacy/hachiko-surround-pr88.glb'),root=doc.getRoot();
const roles=['street_surround_branch','street_surround_needle','street_surround_stone','street_surround_silver','street_surround_panel'];
const removed=[];
for(const name of roles){
  const node=root.listNodes().find(n=>n.getName()===name);if(!node)throw Error('Missing old role '+name);
  let triangles=0;const mesh=node.getMesh();for(const p of mesh.listPrimitives())triangles+=p.getIndices().getCount()/3;
  removed.push({name,triangles,primitives:mesh.listPrimitives().length});node.dispose();mesh.dispose();
}
const usedAccessors=new Set(),usedMaterials=new Set();
for(const mesh of root.listMeshes())for(const p of mesh.listPrimitives()){
  usedMaterials.add(p.getMaterial());usedAccessors.add(p.getIndices());for(const a of p.listAttributes())usedAccessors.add(a);
}
root.listAccessors().filter(a=>!usedAccessors.has(a)).forEach(a=>a.dispose());root.listMaterials().filter(m=>!usedMaterials.has(m)).forEach(m=>m.dispose());
await io.write(base+'web/hachiko-surround.glb',doc);
writeFileSync(base+'source/replaced-roles.json',JSON.stringify({basis:'5e5cc6341ddf00e0f39b3e72d4289f184786df2a',removed,preserved:root.listNodes().filter(n=>n.getMesh()).map(n=>n.getName()),note:'Only nodes belonging to the old surround export. Memorial was already absent; separate memorial GLB untouched.'},null,2)+'\n');
// Preserve original mesh/UV/normal buffers; only encode the four authored maps at
// a runtime resolution. Original 1024 maps and editable source stay in deliveries.
const seat=await io.read(base+'source/deliveries/hachiko_seating_paving_v002/web/current_pair.glb');
for(const t of seat.getRoot().listTextures()){
  const image=execFileSync(process.env.PYTHON??'python',['-c',"import sys,io;from PIL import Image; im=Image.open(io.BytesIO(sys.stdin.buffer.read()));im=im.resize((512,512),Image.Resampling.LANCZOS);out=io.BytesIO();im.save(out,format='PNG',optimize=True);sys.stdout.buffer.write(out.getvalue())"],{input:Buffer.from(t.getImage()),maxBuffer:5_000_000});
  t.setImage(new Uint8Array(image)).setMimeType('image/png');
}
await io.write(base+'web/seating.glb',seat);
