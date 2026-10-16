import {beforeAll,expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {NodeIO,type Document} from '@gltf-transform/core';
import {Matrix4,Vector3,Ray,Mesh,MeshBasicMaterial,MeshStandardMaterial,Texture} from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {loadBuilding,applyEmissive,type BuildingIO} from '../src/world/buildings';
import {applyClassPass,applyLook,CLASS_COLORS,LOOK_DEFAULT} from '../src/world/look';
const dir='assets/buildings/station-north',source=dir+'/source/st-1';
const config=JSON.parse(readFileSync(source+'/placement.json','utf8'));
const report=JSON.parse(readFileSync(source+'/build-report.json','utf8'));
const documents=new Map<string,{input:Document;output:Document}>();
beforeAll(async()=>{const io=new NodeIO();for(const c of config.components)documents.set(c.id,{input:await io.read(source+'/'+c.input),output:await io.read(dir+'/web/'+c.output)});});
const hash=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
async function live(){
 const loader=new GLTFLoader();const path=(u:string)=>u.replace('assets/buildings/station-north/',dir+'/web/');
 const io:BuildingIO={async loadGlb(u){const b=readFileSync(path(u));return (await loader.parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength) as ArrayBuffer,'')).scene;},async loadJson(u){return JSON.parse(readFileSync(path(u),'utf8'));}};
 const b=await loadBuilding('station-north',io,'assets/buildings');if(!b.ok)throw Error(b.error);
 expect(b.layerErrors).toEqual([]);expect(b.layers).toHaveLength(2);return b;
}
function materials(root:import('three').Object3D){const out:MeshStandardMaterial[]=[];root.traverse(o=>{if(o instanceof Mesh)out.push(...(Array.isArray(o.material)?o.material:[o.material]) as MeshStandardMaterial[]);});return out;}
it('preserves station structure and both source surfaces, and keeps generated settings in the manifest',()=>{
 expect(hash(dir+'/web/station-north.glb')).toBe('eb1b9607fa28c0410ada219fd42cbb6f19592ddb2bb6002050869eb5bf65ed09');
 const hints=JSON.parse(readFileSync(dir+'/web/viewer.json','utf8')),manifest=JSON.parse(readFileSync(dir+'/manifest.json','utf8'));
 expect(hints.groundElevationTP).toBe(15);expect(hints.layers).toEqual(Object.fromEntries(config.components.map((c:{layer:string;output:string})=>[c.layer,c.output])));
 for(const path of ['web/viewer.json','source/st-1/placement.json'])expect(manifest.files[path]).toEqual({bytes:readFileSync(dir+'/'+path).length,sha256:hash(dir+'/'+path)});
 for(const c of config.components){
  expect(hash(source+'/'+c.input)).toBe(c.sha256);
  const {input,output}=documents.get(c.id)!,a=input.getRoot(),b=output.getRoot();
  a.listMeshes().forEach((m,i)=>m.listPrimitives().forEach((p,j)=>{
   const q=b.listMeshes()[i].listPrimitives()[j];expect(q.getIndices()?.getArray()).toEqual(p.getIndices()?.getArray());
   for(const attr of p.listSemantics()){
    if(c.id==='centre-pier-cladding' && attr==='POSITION'){
     const a=p.getAttribute(attr)!,b=q.getAttribute(attr)!;
     for(let k=0;k<a.getCount();k++){
      const v=a.getElement(k,[]),w=b.getElement(k,[]);
      if(Math.abs(v[1])<1e-6){expect(w[0]).toBeCloseTo(v[0],5);expect(w[2]).toBeCloseTo(v[2],5);expect(Math.abs(w[1]-v[1])).toBeLessThan(.2);}
      else expect(w).toEqual(v);
     }
    }else expect(q.getAttribute(attr)?.getArray()).toEqual(p.getAttribute(attr)?.getArray());
   }
   const values=(m:NonNullable<ReturnType<typeof p.getMaterial>>)=>[m.getName(),m.getBaseColorFactor(),m.getEmissiveFactor(),m.getDoubleSided()];
   expect(values(q.getMaterial()!)).toEqual(values(p.getMaterial()!));
   const aPos=p.getAttribute('POSITION')!,bPos=q.getAttribute('POSITION')!,idx=q.getIndices();
   for(let k=0;k<(idx?.getCount()??bPos.getCount());k+=3){
    const triangle=(pos:typeof aPos)=>[0,1,2].map(i=>new Vector3().fromArray(pos.getElement(idx?idx.getScalar(k+i):k+i,[])));
    const [a,b,c]=triangle(aPos),[x,y,z]=triangle(bPos),oldNormal=b.clone().sub(a).cross(c.clone().sub(a)),normal=y.clone().sub(x).cross(z.clone().sub(x));
    expect(normal.lengthSq()).toBeGreaterThan(1e-16);expect(oldNormal.dot(normal)).toBeGreaterThan(0);
   }
  }));
  expect(b.listTextures()).toHaveLength(0);expect(b.listAnimations()).toHaveLength(0);
 }
});
it('uses one common positive uniform transform with adjacent fascia/pier edges and the retained soffit',()=>{
 for(const c of config.components){
  const root=documents.get(c.id)!.output.getRoot().listNodes().find(n=>n.getName()==='ST1_'+c.id)!;
  const matrix=new Matrix4().fromArray(root.getWorldMatrix()),scale=new Vector3().setFromMatrixScale(matrix);
  expect(matrix.determinant()).toBeGreaterThan(0);expect(scale.x).toBeCloseTo(scale.y,6);expect(scale.y).toBeCloseTo(scale.z,6);expect(scale.x).toBeCloseTo(config.uniformScale,6);
  matrix.toArray().forEach((v,i)=>expect(v).toBeCloseTo(report.components.find((r:{id:string})=>r.id===c.id).worldMatrix[i],6));
 }
 expect(config.components[0].position[0]+2.4).toBeCloseTo(-1.11,5);expect(config.components[1].position[0]-1.1).toBe(-1.1);
 expect(config.groundY+4.2*config.uniformScale).toBeLessThan(config.soffitY);
 expect(config.components[0].position[1]+1.12).toBeCloseTo(4.2,5);
 for(const c of config.components)for(const n of documents.get(c.id)!.output.getRoot().listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const pos=p.getAttribute('POSITION')!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
  for(let i=0;i<pos.getCount();i++)expect(new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(matrix).z).toBeGreaterThan(16.853);
 }
 const fits=report.components.find((r:{id:string})=>r.id==='centre-pier-cladding').bottomFits;
 expect(fits.length).toBeGreaterThan(0);for(const f of fits)expect(f.groundY-f.newY).toBeCloseTo(.005,7);
});
it('classifies all real fascia primitives as signs and all shallow pier primitives as wall',async()=>{
 const b=await live();applyClassPass(b.root,b.emissive.day);
 for(const c of config.components){const group=b.root.getObjectByName('station-north:'+c.layer)!;expect(group).toBeDefined();const ms=materials(group);expect(ms.length).toBe(c.id==='entry-fascia'?13:3);for(const m of ms)expect((m as unknown as MeshBasicMaterial).color.getHex()).toBe(c.id==='entry-fascia'?CLASS_COLORS.sign:CLASS_COLORS.wall);}
});
it('fits actual exported pier bottom vertices to the unchanged visible terrain',async()=>{
 const root=(await new NodeIO().read('assets/ground/extension/web/extension.glb')).getRoot(),triangles:Vector3[][]=[];
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const pos=p.getAttribute('POSITION')!,idx=p.getIndices(),matrix=new Matrix4().fromArray(n.getWorldMatrix());
  for(let i=0;i<(idx?.getCount()??pos.getCount());i+=3)triangles.push([0,1,2].map(k=>new Vector3().fromArray(pos.getElement(idx?idx.getScalar(i+k):i+k,[])).applyMatrix4(matrix)));
 }
 const {input,output}=documents.get('centre-pier-cladding')!;let checked=0;
 input.getRoot().listMeshes().forEach((mesh,i)=>mesh.listPrimitives().forEach((p,j)=>{
  const outMesh=output.getRoot().listMeshes()[i],q=outMesh.listPrimitives()[j],a=p.getAttribute('POSITION')!,b=q.getAttribute('POSITION')!;
  const n=output.getRoot().listNodes().find(n=>n.getMesh()===outMesh)!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
  for(let k=0;k<a.getCount();k++)if(Math.abs(a.getElement(k,[])[1])<1e-6){
   const point=new Vector3().fromArray(b.getElement(k,[])).applyMatrix4(matrix),ray=new Ray(new Vector3(point.x,50,point.z),new Vector3(0,-1,0));
   const heights=triangles.flatMap(([a,b,c])=>{const hit=ray.intersectTriangle(a,b,c,false,new Vector3());return hit?[hit.y]:[];});
   expect(heights.length).toBeGreaterThan(0);expect(point.y).toBeCloseTo(Math.max(...heights)-.005,5);checked++;
  }
 }));
 expect(checked).toBeGreaterThan(0);
});
it('applies normal day/night look to signs and wall separately using real GLBs',async()=>{
 const b=await live(),env=new Texture();
 const sign=materials(b.root.getObjectByName('station-north:'+config.components[0].layer)!),wall=materials(b.root.getObjectByName('station-north:'+config.components[1].layer)!);
 for(const mode of ['day','night','day','night'] as const){
  applyEmissive(b.root,b.emissive[mode]);applyLook(b.root,mode,{...LOOK_DEFAULT,nightSign:.37},b.emissive.day,{map:env,intensity:2});
  for(const m of sign){expect(m.envMap).toBeNull();expect(m.emissiveIntensity).toBeCloseTo(mode==='night'?.37:1);expect(m.emissive.toArray()).toEqual([0,0,0]);}
  for(const m of wall){expect(m.envMap).toBe(env);expect(m.envMapIntensity).toBe(LOOK_DEFAULT.wallEnv*2);expect(m.emissiveIntensity).toBe(1);}
 }
});
