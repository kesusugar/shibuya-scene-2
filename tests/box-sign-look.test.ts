import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Mesh,MeshBasicMaterial,MeshStandardMaterial,Texture} from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {loadBuilding,applyEmissive,type BuildingIO} from '../src/world/buildings';
import {applyClassPass,applyLook,CLASS_COLORS,LOOK_DEFAULT} from '../src/world/look';
const dir='assets/buildings/shibu-hachi-box';
const placement=JSON.parse(readFileSync(dir+'/source/exterior-signs/placement.json','utf8'));
it('keeps the generated settings and source covered by the asset manifest',()=>{
 const manifest=JSON.parse(readFileSync(dir+'/manifest.json','utf8'));
 for(const path of ['web/viewer.json','source/exterior-signs/placement.json']){
  const bytes=readFileSync(dir+'/'+path);
  expect(manifest.files[path]).toEqual({bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
 }
});
async function load(){
 const loader=new GLTFLoader();
 // Decode the actual geometry/hierarchy/PBR materials with Three. Only browser
 // image decoding is replaced; original image bytes/UVs are tested in box-exterior.
 loader.register(()=>({name:'node-image-decoder',loadTexture:async()=>new Texture()}));
 const path=(url:string)=>url.replace('assets/buildings/shibu-hachi-box/',dir+'/web/');
 const io:BuildingIO={
  async loadGlb(url){const b=readFileSync(path(url));return (await loader.parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength) as ArrayBuffer,'')).scene;},
  async loadJson(url){return JSON.parse(readFileSync(path(url),'utf8'));},
 };
 const b=await loadBuilding('shibu-hachi-box',io,'assets/buildings');
 if(!b.ok)throw new Error(b.error);
 expect(b.layerErrors).toEqual([]);expect(b.layers).toHaveLength(6);
 return b;
}
function meshes(root:import('three').Object3D){const result:Mesh[]=[];root.traverse(o=>{if(o instanceof Mesh)result.push(o);});return result;}
it('classifies every real BOX-2 layer primitive as signage through the production loader',async()=>{
 const b=await load();
 expect(b.hints.layers).toEqual(Object.fromEntries(placement.components.map((c:{layer:string;output:string})=>[c.layer,c.output])));
 applyClassPass(b.root,b.emissive.day);
 let count=0;
 for(const c of placement.components){
  expect(c.layer.startsWith('signs_')).toBe(true);
  const layer=b.root.getObjectByName('shibu-hachi-box:'+c.layer)!;
  expect(layer).toBeDefined();const parts=meshes(layer);expect(parts.length).toBeGreaterThan(0);
  for(const m of parts)for(const mat of Array.isArray(m.material)?m.material:[m.material]){
   expect((mat as MeshBasicMaterial).color.getHex(),c.id+'/'+m.name).toBe(CLASS_COLORS.sign);count++;
  }
 }
 expect(count).toBe(16);
 // The building shell still contains walls; classification was not broadened.
 expect(meshes(b.root.children[0]).some(m=>(m.material as MeshBasicMaterial).color.getHex()===CLASS_COLORS.wall)).toBe(true);
});
it('keeps real sign materials out of wall reflections and applies non-default nightSign',async()=>{
 const b=await load(),env=new Texture(),look={...LOOK_DEFAULT,nightSign:.37};
 const materials:MeshStandardMaterial[][]=placement.components.map((c:{layer:string})=>meshes(b.root.getObjectByName('shibu-hachi-box:'+c.layer)!).flatMap(m=>Array.isArray(m.material)?m.material:[m.material]) as MeshStandardMaterial[]);
 for(const mode of ['day','night'] as const){
  applyEmissive(b.root,b.emissive[mode]);
  const before=materials.map(ms=>ms.map(m=>({intensity:m.emissiveIntensity,env:m.envMapIntensity})));
  applyLook(b.root,mode,look,b.emissive.day,{map:env,intensity:2});
  materials.forEach((ms,i)=>ms.forEach((m,j)=>{
   expect(m.envMap).toBeNull();expect(m.envMapIntensity).toBe(before[i][j].env);
   expect(m.emissiveIntensity).toBeCloseTo(before[i][j].intensity*(mode==='night'?.37:1));
  }));
 }
 expect(meshes(b.root.children[0]).some(m=>(m.material as MeshStandardMaterial).envMap===env)).toBe(true);
});
