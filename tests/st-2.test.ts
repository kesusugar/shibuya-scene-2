import {beforeAll,expect,it} from 'vitest';
import {NodeIO,type Document} from '@gltf-transform/core';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Matrix4,Vector3,Raycaster,Mesh,MeshBasicMaterial,MeshStandardMaterial,Texture} from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {loadBuilding,applyEmissive,type BuildingIO} from '../src/world/buildings';
import {applyClassPass,applyLook,CLASS_COLORS,LOOK_DEFAULT,classify} from '../src/world/look';
const station='assets/buildings/station-north',dir='assets/buildings/hachiko-policebox',source=dir+'/source/st-2';
const config=JSON.parse(readFileSync(station+'/source/st-2/opening.json','utf8')),report=JSON.parse(readFileSync(station+'/source/st-2/build-report.json','utf8'));
const placement=JSON.parse(readFileSync(source+'/placement.json','utf8')),facade=JSON.parse(readFileSync(source+'/build-report.json','utf8'));
const hash=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
let old:Document,live:Document;
beforeAll(async()=>{const io=new NodeIO();old=await io.read(station+'/source/st-2/'+config.baseline);live=await io.read(station+'/web/station-north.glb');});
it('pins the verified original ZIP receipt, source GLB and PR82 shell, and keeps all ST-1 layers/configuration',()=>{
 const receipt=JSON.parse(readFileSync(source+'/delivery-verification.json','utf8'));
 expect(receipt.zipBytes).toBe(6061533);expect(receipt.zipSha256).toBe('575d5eddc484263e43f314b12309c9c92e84d190e6912deceefe3fc10b3e7dfa');expect(receipt.allCRCValid&&receipt.safePaths).toBe(true);expect(receipt.manifestCount).toBe(18);
 expect(hash(source+'/policebox_visible_facade_2025_v001.glb')).toBe(placement.sourceSha256);expect(hash(station+'/source/st-2/'+config.baseline)).toBe(config.baselineSha256);
 expect(config.baselineSha256).toBe('ecd9095e10082dd166ef2291df775532d4b5019390b4094abaa1b7c551644649');expect(hash(station+'/web/station-north.glb')).toBe(report.outputSha256);
 const pins=JSON.parse(readFileSync(station+'/source/st-1-opening/opening.json','utf8')).preservedST1Files;
 for(const [path,sha] of Object.entries(pins))expect(hash(station+'/'+path),path).toBe(sha);
 for(const root of [dir,station]){const manifest=JSON.parse(readFileSync(root+'/manifest.json','utf8'));for(const [p,row] of Object.entries(manifest.files))expect(row,p).toEqual({bytes:readFileSync(root+'/'+p).length,sha256:hash(root+'/'+p)});}
});
it('changes only two approved west-face triangles and preserves the entire PR82 JR entrance, roof and station structure',()=>{
 const a=old.getRoot(),b=live.getRoot();expect(b.listNodes()).toHaveLength(a.listNodes().length+1);
 for(const node of a.listNodes()){
  const out=b.listNodes().find(n=>n.getName()===node.getName())!;expect(out.getMatrix()).toEqual(node.getMatrix());
  node.getMesh()?.listPrimitives().forEach((p,j)=>{
   const q=out.getMesh()!.listPrimitives()[j],changed=(node.getName()===config.targetNode||node.getName()==='stn_hoarding')&&j===0;
   for(const key of p.listSemantics()){const x=p.getAttribute(key)!.getArray()!,y=q.getAttribute(key)!.getArray()!;expect(Array.from(changed?y.slice(0,x.length):y)).toEqual(Array.from(x));}
   const x=Array.from(p.getIndices()!.getArray()! as ArrayLike<number>),y=Array.from(q.getIndices()!.getArray()! as ArrayLike<number>);
   if(!changed)expect(y).toEqual(x);else{
    const expected:number[]=[],retained:number[]=[],count=p.getAttribute('POSITION')!.getCount();
    for(let k=0;k<x.length;k+=3)if(!(node.getName()==='stn_hoarding'?[0,3]:config.targetTriangles).includes(k/3))expected.push(...x.slice(k,k+3));
    for(let k=0;k<y.length;k+=3)if(y.slice(k,k+3).every(i=>i<count))retained.push(...y.slice(k,k+3));
    expect(retained).toEqual(expected);expect(report.cuts.map((r:{triangle:number})=>r.triangle)).toEqual([0,507]);
   }
   expect(q.getMaterial()!.getBaseColorFactor()).toEqual(p.getMaterial()!.getBaseColorFactor());
  });
 }
});
it('merges source components without changing their triangles and applies the same uniform site transform once',async()=>{
 const io=new NodeIO(),raw=await io.read(source+'/policebox_visible_facade_2025_v001.glb');
 const outputs:Document[]=await Promise.all(facade.components.map((c:{file:string})=>io.read(dir+'/web/'+c.file)));
 for(const [di,d] of outputs.entries()){
  const component=facade.components[di],names=new Set(component.nodes),groups=new Map<string,number[]>(),expectedIndices=new Map<string,number[]>();
  for(const n of raw.getRoot().listNodes())if(names.has(n.getName()))for(const p of n.getMesh()?.listPrimitives()??[]){
   const key=p.getMaterial()!.getName(),values=groups.get(key)??[],offset=values.length/3;groups.set(key,values);
   const indices=expectedIndices.get(key)??[];expectedIndices.set(key,indices);for(const index of p.getIndices()!.getArray()!)indices.push(index+offset);
   const matrix=new Matrix4().fromArray(n.getWorldMatrix()),pos=p.getAttribute('POSITION')!;
   for(let i=0;i<pos.getCount();i++)values.push(...new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(matrix).toArray());
  }
  const positions=d.getRoot().listMeshes().flatMap(m=>m.listPrimitives()).map(p=>Array.from(p.getAttribute('POSITION')!.getArray()!));
  expect(positions).toEqual([...groups.values()].map(v=>Array.from(new Float32Array(v))));
  expect(d.getRoot().listMeshes().flatMap(m=>m.listPrimitives()).map(p=>Array.from(p.getIndices()!.getArray()!))).toEqual([...expectedIndices.values()]);
  d.getRoot().listNodes().find(n=>n.getName()==='ST2_site_transform')!.getMatrix().forEach((v,i)=>expect(v).toBeCloseTo(report.worldMatrix[i],12));expect(d.getRoot().listTextures()).toHaveLength(0);
 }

 expect(facade.stats).toMatchObject({triangles:12088,primitives:11});expect(placement.uniformScale).toBe(1);
});
it('leaves a real shallow opening behind the facade, with closed back and oblique reveals rather than an uncut wall',async()=>{
 const bytes=readFileSync(station+'/web/station-north.glb'),g=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength) as ArrayBuffer,'');g.scene.updateMatrixWorld(true);
 const w=new Matrix4().fromArray(report.worldMatrix),inv=w.clone().invert();
 const hit=(x:number,y:number,z:number,d:Vector3)=>new Raycaster(new Vector3(x,y,z).applyMatrix4(w),d.transformDirection(w),0,5).intersectObject(g.scene,true)[0];
 for(const x of [-2,0,2])for(const y of [.8,2,5.5])expect(hit(x,y,2,new Vector3(0,0,-1)).point.clone().applyMatrix4(inv).z).toBeCloseTo(-.74,4);
 for(const [x,dx] of [[-2,-1],[2,1]])expect(hit(x,2,-.1,new Vector3(dx,0,-.1)).point.clone().applyMatrix4(inv).x).toBeCloseTo(dx*2.6,4);
 expect(hit(0,2,-1,new Vector3(0,0,1)).point.clone().applyMatrix4(inv).z).toBeCloseTo(-.74,4);
 expect(report.noFloorOrWalkSurfaceAdded&&report.collisionCodeUnchanged).toBe(true);expect(report.walkableEntrance).toBe(false);
});
it('uses the normal loader and existing sign/glass/wall classes through day/night/day',async()=>{
 const loader=new GLTFLoader(),io:BuildingIO={async loadGlb(url){const p=url.replace('assets/buildings/hachiko-policebox/',dir+'/web/'),b=readFileSync(p);return (await loader.parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength) as ArrayBuffer,'')).scene;},async loadJson(url){return JSON.parse(readFileSync(url.replace('assets/buildings/hachiko-policebox/',dir+'/web/'),'utf8'));}};
 const b=await loadBuilding('hachiko-policebox',io,'assets/buildings');if(!b.ok)throw Error(b.error);expect(b.layerErrors).toEqual([]);expect(b.layers).toEqual(['signs_2025-04-09']);
 const classes=new Map<Mesh,string>();b.root.traverse(o=>{if(o instanceof Mesh){let p:import('three').Object3D|null=o,sign=false;while(p){sign ||= /:signs/.test(p.name);p=p.parent;}classes.set(o,classify(o.material as MeshStandardMaterial,o.name,b.emissive.day,sign));}});
 expect([...classes.values()].filter(v=>v==='sign')).toHaveLength(3);expect([...classes.values()].filter(v=>v==='glass')).toHaveLength(1);expect([...classes.values()].filter(v=>v==='wall')).toHaveLength(7);
 for(const mode of ['day','night','day'] as const){applyEmissive(b.root,b.emissive[mode]);applyLook(b.root,mode,LOOK_DEFAULT,b.emissive[mode],{map:new Texture(),intensity:1});for(const [mesh,c] of classes){const m=mesh.material as MeshStandardMaterial;expect(m.emissive.toArray()).toEqual([0,0,0]);if(c!=='sign')expect(m.envMapIntensity).toBe(c==='glass'?LOOK_DEFAULT.glassEnv:LOOK_DEFAULT.wallEnv);}}
 applyClassPass(b.root,b.emissive.day);for(const [mesh,c] of classes)expect((mesh.material as MeshBasicMaterial).color.getHex()).toBe(CLASS_COLORS[c as keyof typeof CLASS_COLORS]);
});
