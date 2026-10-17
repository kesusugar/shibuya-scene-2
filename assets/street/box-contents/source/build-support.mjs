// Local technical lower apron joining the delivered TKTS upper cutoff to the
// accepted BOX floor. Estimated continuation, NOT recovered cabinet internals.
// Run from repo root: node assets/street/box-contents/source/build-support.mjs
import { Document, NodeIO } from '@gltf-transform/core';
import { BoxGeometry } from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
const geometries = [
  [[1.4,.7,.052],[0,.35,.454]],
  [[.052,.7,.908],[.674,.35,-.026]],
  [[.052,.7,.760],[-.446,.35,-.100]],
].map(([size, center]) => new BoxGeometry(...size).translate(...center));
const g = mergeGeometries(geometries);
const io = new NodeIO(), doc = new Document(), buffer = doc.createBuffer();
const delivered = await io.read('assets/street/box-contents/web/tkts.glb');
const red = delivered.getRoot().listMaterials().find(m=>/red/i.test(m.getName()));
if(!red) throw Error('Missing delivered red material');
const mat = doc.createMaterial('street_box_estimated_lower_red_apron').setBaseColorFactor(red.getBaseColorFactor()).setRoughnessFactor(red.getRoughnessFactor()).setMetallicFactor(red.getMetallicFactor());
const p = doc.createPrimitive().setMaterial(mat);
for(const [name, attr] of [['POSITION','position'],['NORMAL','normal']]) p.setAttribute(name,doc.createAccessor().setType('VEC3').setArray(g.getAttribute(attr).array).setBuffer(buffer));
p.setIndices(doc.createAccessor().setType('SCALAR').setArray(g.index.array).setBuffer(buffer));
doc.createScene().addChild(doc.createNode('Estimated_lower_apron_no_cabinet_interiors').setMesh(doc.createMesh().addPrimitive(p)));
await io.write('assets/street/box-contents/web/tkts-support.glb',doc);
