// Usage: node check_loader.mjs model.glb /absolute/repository/node_modules/three/examples/jsm/loaders/GLTFLoader.js
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const {GLTFLoader}=await import(pathToFileURL(process.argv[3]).href);
const raw=fs.readFileSync(process.argv[2]);
const gltf=await new Promise((resolve,reject)=>new GLTFLoader().parse(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'',resolve,reject));
let meshes=0,triangles=0,colors=0,materials=new Set(),nonfinite=0;
const names=[];
gltf.scene.traverse(o=>{if(!o.isMesh)return;meshes++;names.push(o.name);triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3; if(o.geometry.attributes.color)colors++;materials.add(o.material.uuid);for(const a of Object.values(o.geometry.attributes))for(const v of a.array)if(!Number.isFinite(v))nonfinite++;});
if(nonfinite)throw new Error('Nonfinite active attributes');
if(names.includes('shibuya109_canopy_under')||names.includes('shibuya109_entrance_sign_panel'))throw new Error('Obsolete entrance imported');
console.log(JSON.stringify({loader:'Three.js GLTFLoader',meshes,triangles,materialCount:materials.size,colorAttributeMeshes:colors,nonfinite,names,scope:'Asset-level loader verification only; no full-game/current-main claim'},null,2));
