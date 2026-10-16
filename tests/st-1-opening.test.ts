import {beforeAll,expect,it} from 'vitest';
import {NodeIO,type Document} from '@gltf-transform/core';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Matrix4,Vector3,Raycaster,Mesh,MeshBasicMaterial,MeshStandardMaterial,Texture} from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {applyClassPass,applyLook,CLASS_COLORS,LOOK_DEFAULT} from '../src/world/look';
import {applyEmissive} from '../src/world/buildings';
const dir='assets/buildings/station-north',source=dir+'/source/st-1-opening';
const config=JSON.parse(readFileSync(source+'/opening.json','utf8')),report=JSON.parse(readFileSync(source+'/build-report.json','utf8'));
const hash=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
let old:Document,live:Document;
beforeAll(async()=>{const io=new NodeIO();old=await io.read(source+'/'+config.baseline);live=await io.read(dir+'/web/station-north.glb');});
it('preserves the original GLB and unchanged ST-1 placement, sign, pier and day/night settings',()=>{
 expect(hash(source+'/'+config.baseline)).toBe(config.baselineSha256);expect(hash(dir+'/web/station-north.glb')).toBe(report.outputSha256);
 for(const [path,sha] of Object.entries(config.preservedST1Files))expect(hash(dir+'/'+path),path).toBe(sha);
 const manifest=JSON.parse(readFileSync(dir+'/manifest.json','utf8'));
 for(const path of ['web/station-north.glb','source/st-1-opening/opening.json','source/st-1-opening/'+config.baseline])expect(manifest.files[path]).toEqual({bytes:readFileSync(dir+'/'+path).length,sha256:hash(dir+'/'+path)});
});
it('keeps all original triangles and attributes outside the two explicitly approved source triangles',()=>{
 const a=old.getRoot(),b=live.getRoot();
 expect(b.listNodes()).toHaveLength(a.listNodes().length+1);expect(b.listMeshes()).toHaveLength(a.listMeshes().length+1);
 for(const node of a.listNodes()){
  const out=b.listNodes().find(n=>n.getName()===node.getName())!;expect(out).toBeDefined();expect(out.getMatrix()).toEqual(node.getMatrix());
  node.getMesh()?.listPrimitives().forEach((p,j)=>{
   const q=out.getMesh()!.listPrimitives()[j],changed=node.getName()===config.targetNode && j===config.targetPrimitive;
   for(const attr of p.listSemantics()){
    const before=p.getAttribute(attr)!.getArray()!,after=q.getAttribute(attr)!.getArray()!;
    expect(Array.from(changed?after.slice(0,before.length):after),node.getName()+'/'+attr).toEqual(Array.from(before));
   }
   expect(q.getMaterial()!.getName()).toBe(p.getMaterial()!.getName());expect(q.getMaterial()!.getBaseColorFactor()).toEqual(p.getMaterial()!.getBaseColorFactor());
   const before=Array.from(p.getIndices()!.getArray()! as ArrayLike<number>),after=Array.from(q.getIndices()!.getArray()! as ArrayLike<number>);
   if(!changed)expect(after).toEqual(before);
   else{
    const count=p.getAttribute('POSITION')!.getCount(),expected:number[]=[],retained:number[]=[];
    for(let k=0;k<before.length;k+=3)if(!config.targetTriangles.includes(k/3))expected.push(...before.slice(k,k+3));
    for(let k=0;k<after.length;k+=3)if(after.slice(k,k+3).every(i=>i<count))retained.push(...after.slice(k,k+3));
    expect(retained).toEqual(expected);
    expect(report.cuts.map((c:{triangle:number})=>c.triangle)).toEqual([94,95]);expect(report.removedArea).toBeGreaterThan(16);expect(report.removedArea).toBeLessThan(17);
    const area=(p:typeof q)=>{
     const pos=p.getAttribute('POSITION')!,idx=p.getIndices()!;let sum=0;
     for(let k=0;k<idx.getCount();k+=3){const [a,b,c]=[0,1,2].map(i=>new Vector3().fromArray(pos.getElement(idx.getScalar(k+i),[])));sum+=b.sub(a).cross(c.sub(a)).length()/2;}
     return sum;
    };
    expect(area(p)-area(q)).toBeCloseTo(report.removedArea,2);
   }
  });
 }
 // Removing a small wall patch must not drop or change the original roof, canopy, support materials or hidden structure.
 a.listMaterials().forEach((m,i)=>{const n=b.listMaterials()[i];expect(n.getName()).toBe(m.getName());expect(n.getBaseColorFactor()).toEqual(m.getBaseColorFactor());expect(n.getEmissiveFactor()).toEqual(m.getEmissiveFactor());expect(n.getRoughnessFactor()).toBe(m.getRoughnessFactor());expect(n.getMetallicFactor()).toBe(m.getMetallicFactor());});
});
it('opens the actual GLB only below the fascia and closes a shallow recess with real side reveals and a back',async()=>{
 const bytes=readFileSync(dir+'/web/station-north.glb'),g=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength) as ArrayBuffer,'');
 const baseline=readFileSync(source+'/'+config.baseline),prior=await new GLTFLoader().parseAsync(baseline.buffer.slice(baseline.byteOffset,baseline.byteOffset+baseline.byteLength) as ArrayBuffer,'');prior.scene.updateMatrixWorld(true);
 g.scene.updateMatrixWorld(true);const world=new Matrix4().fromArray(report.worldMatrix),inverse=world.clone().invert();
 const point=(x:number,y:number,z:number)=>new Vector3(x,y,z).applyMatrix4(world);
 const hit=(x:number,y:number,z:number,direction:Vector3)=>new Raycaster(point(x,y,z),direction.transformDirection(world),0,5).intersectObject(g.scene,true)[0];
 for(const x of [-5.8,-4,-1.2])for(const y of [.3,1.3,2.8,3.05]){
  const h=hit(x,y,.5,new Vector3(0,0,-1));expect(h).toBeDefined();expect((h.object as Mesh).material).toBeDefined();
  expect(h.point.clone().applyMatrix4(inverse).z).toBeCloseTo(config.wallPlaneZ-config.depth,4);
 }
 for(const x of [-6,-.9])expect(hit(x,1.5,.5,new Vector3(0,0,-1)).point.clone().applyMatrix4(inverse).z).toBeCloseTo(config.wallPlaneZ,3);
 expect(hit(-3,3.15,.5,new Vector3(0,0,-1)).point.clone().applyMatrix4(inverse).z).toBeCloseTo(config.wallPlaneZ,3);
 for(const x of [-45,-25,-10,-6,-.9,2,5,10,20])for(const y of [.3,1.3,2.8,3.15,4.6]){
  const ray=new Raycaster(point(x,y,.5),new Vector3(0,0,-1).transformDirection(world),0,5),a=ray.intersectObject(prior.scene,true)[0],b=ray.intersectObject(g.scene,true)[0];
  if(!a)expect(b).toBeUndefined();else{expect(b).toBeDefined();expect(b.distance).toBeCloseTo(a.distance,4);}
 }
 // Oblique lines hit actual left/right reveal geometry before reaching the back.
 for(const sign of [-1,1]){
  const h=hit(sign<0?-5.5:-1.5,1.5,-.15,new Vector3(sign,0,-.1));
  expect(h.point.clone().applyMatrix4(inverse).x).toBeCloseTo(sign<0?config.xMin:config.xMax,4);
 }
 const reverse=hit(-3,1.5,-1,new Vector3(0,0,1));expect(reverse.point.clone().applyMatrix4(inverse).z).toBeCloseTo(config.wallPlaneZ-config.depth,4);
 const recess=g.scene.getObjectByName('ST1_shallow_entry_recess')!,materials:MeshStandardMaterial[]=[];
 recess.traverse(o=>{if(o instanceof Mesh)materials.push(...(Array.isArray(o.material)?o.material:[o.material]) as MeshStandardMaterial[]);});
 expect(materials).toHaveLength(2);for(const m of materials){expect(m.opacity).toBe(1);expect(m.transparent).toBe(false);expect(m.emissive.toArray()).toEqual([0,0,0]);}
 for(const mode of ['day','night','day'] as const){applyEmissive(g.scene,JSON.parse(readFileSync(dir+'/web/emissive_'+mode+'.json','utf8')));applyLook(g.scene,mode,LOOK_DEFAULT,undefined,{map:new Texture(),intensity:1});for(const m of materials){expect(m.emissive.toArray()).toEqual([0,0,0]);expect(m.envMapIntensity).toBe(LOOK_DEFAULT.wallEnv);}}
 applyClassPass(g.scene);recess.traverse(o=>{if(o instanceof Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])expect((m as MeshBasicMaterial).color.getHex()).toBe(CLASS_COLORS.wall);});
 expect(report.noFloorOrWalkSurfaceAdded).toBe(true);expect(report.walkableEntrance).toBe(false);
});
