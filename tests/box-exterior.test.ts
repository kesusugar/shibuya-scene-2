import {describe,it,expect,beforeAll} from 'vitest';
import {NodeIO, type Document} from '@gltf-transform/core';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Matrix4,Vector3,Box3} from 'three';
const dir='assets/buildings/shibu-hachi-box';
const config=JSON.parse(readFileSync(dir+'/source/exterior-signs/placement.json','utf8'));
const report=JSON.parse(readFileSync(dir+'/source/exterior-signs/build-report.json','utf8'));
const approved=JSON.parse(readFileSync(dir+'/source/placement-and-build.json','utf8'));
const basis=new Matrix4().makeRotationX(-Math.PI/2);
const bodyWorld=basis.clone().multiply(new Matrix4().set(...approved.world_matrix_rows.flat() as Parameters<Matrix4['set']>)).multiply(basis.clone().invert());
const hash=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
const documents=new Map<string,{input:Document;output:Document}>();
beforeAll(async()=>{const io=new NodeIO();for(const c of config.components)documents.set(c.id,{input:await io.read(dir+'/source/exterior-signs/'+c.input),output:await io.read(dir+'/web/'+c.output)});});
function bounds(id:string){
 const box=new Box3();for(const n of documents.get(id)!.output.getRoot().listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const a=p.getAttribute('POSITION')!,m=bodyWorld.clone().invert().multiply(new Matrix4().fromArray(n.getWorldMatrix()));
  for(let i=0;i<a.getCount();i++)box.expandByPoint(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m));
 }return box;
}
describe('BOX-2 exterior layers',()=>{
 it('keeps approved body/terrain placement and registers exactly the selected six layers',()=>{
  expect(hash(dir+'/web/shibu-hachi-box.glb')).toBe('c1b262ee107e8b46baad917f30aff885420a8ac611f071b67469b542a18f7a5e');
  const hints=JSON.parse(readFileSync(dir+'/web/viewer.json','utf8'));
  expect(hints.groundElevationTP).toBe(15);
  expect(Object.values(hints.layers).sort()).toEqual(config.components.map((c:{output:string})=>c.output).sort());
  expect(config.components).toHaveLength(6);
  expect(config.components.every((c:{input:string})=>!/(rail_|terrace|counter|shelf)/.test(c.input))).toBe(true);
 });
 it('preserves all source positions, normals, indices, textured UVs and original clock pixels',()=>{
  for(const c of config.components){
   expect(hash(dir+'/source/exterior-signs/'+c.input)).toBe(c.sha256);
   const {input,output}=documents.get(c.id)!,a=input.getRoot(),b=output.getRoot();
   expect(b.listMeshes()).toHaveLength(a.listMeshes().length);
   a.listMeshes().forEach((m,i)=>m.listPrimitives().forEach((p,j)=>{
    const q=b.listMeshes()[i].listPrimitives()[j];
    for(const attr of ['POSITION','NORMAL'])expect(q.getAttribute(attr)?.getArray()).toEqual(p.getAttribute(attr)?.getArray());
    expect(q.getIndices()?.getArray()).toEqual(p.getIndices()?.getArray());
    if(p.getMaterial()?.getBaseColorTexture())expect(q.getAttribute('TEXCOORD_0')?.getArray()).toEqual(p.getAttribute('TEXCOORD_0')?.getArray());
   }));
   expect(b.listTextures()).toHaveLength(a.listTextures().length);
   a.listTextures().forEach((t,i)=>expect(b.listTextures()[i].getImage()).toEqual(t.getImage()));
   for(const m of a.listMaterials()){
    const q=b.listMaterials().find(n=>n.getName()===m.getName())!;
    expect(q.getBaseColorFactor()).toEqual(m.getBaseColorFactor());
    expect(q.getRoughnessFactor()).toBe(m.getRoughnessFactor());expect(q.getMetallicFactor()).toBe(m.getMetallicFactor());
    expect(q.getAlphaMode()).toBe(m.getAlphaMode());expect(q.getDoubleSided()).toBe(m.getDoubleSided());
    expect(q.getEmissiveFactor()).toEqual(c.emissiveFactor??m.getEmissiveFactor());
   }
   expect(b.listAnimations()).toHaveLength(0);
  }
  expect(report.components.find((c:{id:string})=>c.id==='display-clock').removedUnusedUVAccessors).toBe(4);
 });
 it('applies one positive, uniform attachment transform, with the clock facing the short end',()=>{
  for(const c of config.components){
   const root=documents.get(c.id)!.output.getRoot().listNodes().filter(n=>n.getName()===c.id);
   expect(root).toHaveLength(1);
   const matrix=new Matrix4().fromArray(root[0].getWorldMatrix());
   const expected=report.components.find((r:{id:string})=>r.id===c.id).worldMatrix;
   matrix.toArray().forEach((v,i)=>expect(v).toBeCloseTo(expected[i],5));
   expect(matrix.determinant()).toBeGreaterThan(0);
   expect(c.scale[0]).toBe(c.scale[1]);expect(c.scale[1]).toBe(c.scale[2]);
   const front=new Vector3(0,0,1).transformDirection(matrix);
   const target=new Vector3(...(c.id==='display-clock'?[-1,0,0]:[0,0,1]) as [number,number,number]).transformDirection(bodyWorld);
   expect(front.dot(target)).toBeGreaterThan(.99999);
  }
 });
 it('fits roof baselines, the right-bay header and clock clearances without moving the shell',()=>{
  for(const id of ['roof-circle','roof-existing-name','roof-dog','roof-sponsor'])expect(bounds(id).min.y).toBeCloseTo(2.807,4);
  expect(bounds('roof-circle').max.x).toBeLessThan(bounds('roof-existing-name').min.x);
  expect(bounds('roof-existing-name').max.x).toBeLessThan(bounds('roof-dog').min.x);
  expect(bounds('roof-dog').max.x).toBeLessThan(bounds('roof-sponsor').min.x);
  const fun=bounds('fun-project');expect(fun.min.x).toBeGreaterThan(2.2765);expect(fun.max.x).toBeLessThan(6.0545);expect(fun.max.y).toBeLessThan(2.66);expect(fun.min.z-.601).toBeGreaterThan(.0008);
  const clock=bounds('display-clock');expect(clock.min.y).toBeCloseTo(.248,5);
  expect(clock.min.x+6.099).toBeGreaterThan(.23);expect(clock.min.z+1.706).toBeGreaterThan(.24);expect(.518-clock.max.z).toBeGreaterThan(.23);expect(2.66-clock.max.y).toBeGreaterThan(.16);
 });
});
