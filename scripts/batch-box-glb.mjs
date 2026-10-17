// Lossless material grouping for authored static accessories. Does not regenerate
// models or merge materials with different colours, alpha or texture bindings.
import {NodeIO} from '@gltf-transform/core';
import {BufferGeometry, BufferAttribute, Matrix4} from 'three';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';
export async function batchGlb(input, output, placements = [new Matrix4()]) {
  const io = new NodeIO(), doc = await io.read(input), root = doc.getRoot();
  const oldNodes=root.listNodes(), oldMeshes=root.listMeshes(), oldAccessors=root.listAccessors();
  const groups=new Map();
  for(const placement of placements) for(const n of oldNodes) for(const p of n.getMesh()?.listPrimitives()??[]) {
    if(p.getMode()!==4 || p.listSemantics().some(s=>!['POSITION','NORMAL','TEXCOORD_0'].includes(s))) throw Error('Unsupported static primitive');
    const g=new BufferGeometry();
    for(const [semantic,attribute] of [['POSITION','position'],['NORMAL','normal'],['TEXCOORD_0','uv']]) {
      const a=p.getAttribute(semantic);if(a)g.setAttribute(attribute,new BufferAttribute(a.getArray().slice(),a.getElementSize()));
    }
    if(!g.getAttribute('uv'))g.setAttribute('uv',new BufferAttribute(new Float32Array(g.getAttribute('position').count*2),2));
    const idx=p.getIndices();if(idx)g.setIndex(new BufferAttribute(idx.getArray().slice(),1));
    g.applyMatrix4(placement.clone().multiply(new Matrix4().fromArray(n.getWorldMatrix())));
    const mat=p.getMaterial();if(!groups.has(mat))groups.set(mat,[]);groups.get(mat).push(g);
  }
  for(const s of root.listScenes())for(const n of s.listChildren())s.removeChild(n);
  const scene=root.listScenes()[0],buffer=root.listBuffers()[0]??doc.createBuffer();
  for(const [material,geometries] of groups){
    const g=mergeGeometries(geometries),p=doc.createPrimitive().setMaterial(material);
    for(const [semantic,attribute] of [['POSITION','position'],['NORMAL','normal'],['TEXCOORD_0','uv']]){
      const a=g.getAttribute(attribute);if(a)p.setAttribute(semantic,doc.createAccessor().setType(a.itemSize===2?'VEC2':'VEC3').setArray(a.array).setBuffer(buffer));
    }
    p.setIndices(doc.createAccessor().setType('SCALAR').setArray(g.index.array).setBuffer(buffer));
    scene.addChild(doc.createNode(`batch_${material.getName()}`).setMesh(doc.createMesh().addPrimitive(p)));
  }
  oldNodes.forEach(n=>n.dispose());oldMeshes.forEach(m=>m.dispose());oldAccessors.forEach(a=>a.dispose());
  await io.write(output,doc);
}
