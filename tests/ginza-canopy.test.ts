import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,BufferGeometry,Float32BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Raycaster} from 'three';
const base='assets/buildings/ginza-canopy/';
it('replaces the source once while retaining one C station candidate and recording inferred floor levels',()=>{
 const c=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 expect(c.buildings.some((b:{id:string})=>b.id==='way/810356690')).toBe(false);expect(c.excluded.filter((b:{id:string})=>b.id==='way/810356690')).toHaveLength(1);
 expect(c.buildings.filter((b:{group:string})=>b.group==='station')).toHaveLength(1);
 const s=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));expect(s.floor_reference_tp_m).toEqual([28.125,29.531]);expect(s.floor_status).toContain('not measured');
 expect(JSON.parse(readFileSync(base+'web/viewer.json','utf8')).groundElevationTP).toBe(15);
});
it('retains all source roof vertices and a curved M frame below the upper deck',async()=>{
 const root=(await new NodeIO().read(base+'web/ginza-canopy.glb')).getRoot(),roof:Vector3[]=[],arch:Vector3[]=[];
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){
  const target=p.getMaterial()!.getName()==='gc_roof'?roof:p.getMaterial()!.getName()==='gc_arch'?arch:null;if(!target)continue;
  const a=p.getAttribute('POSITION')!,world=new Matrix4().fromArray(n.getWorldMatrix());for(let i=0;i<a.getCount();i++)target.push(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(world));
 }
 const parts=JSON.parse(readFileSync(base+'source/data/parts.json','utf8'));
 for(const s of parts[0].surfaces.filter((s:{kind:string})=>s.kind==='RoofSurface'))for(const p of s.ring)expect(roof.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.001)).toBe(true);
 const length=Math.hypot(86.172,28.711),local=(v:Vector3)=>(v.x-122.486)*(-28.711/length)+(-v.z+67.458)*(86.172/length);
 const peak=arch.filter(v=>Math.abs(local(v))<.22),valley=arch.filter(v=>Math.abs(local(v)+5.85)<.22);
 expect(Math.max(...peak.map(v=>v.y))).toBeGreaterThan(20);expect(Math.max(...valley.map(v=>v.y))).toBeLessThan(19.4);
 expect(Math.max(...arch.map(v=>v.y))).toBeLessThanOrEqual(20.5);
});
it('opens the upper hall with transparent screen doors while retaining the lower base',async()=>{
 const root=(await new NodeIO().read(base+'web/ginza-canopy.glb')).getRoot(),meshes:Mesh[]=[],material=new MeshBasicMaterial({side:DoubleSide});
 const glass=root.listMaterials().find(m=>m.getName()==='gc_glass')!;expect(glass.getAlphaMode()).toBe('BLEND');expect(glass.getBaseColorFactor()[3]).toBeLessThan(1);
 try{
  for(const n of root.listNodes())for(const prim of n.getMesh()?.listPrimitives()??[]){
   const a=prim.getAttribute('POSITION')!,idx=prim.getIndices(),world=new Matrix4().fromArray(n.getWorldMatrix()),pts:number[]=[];
   for(let i=0;i<(idx?.getCount()??a.getCount());i++){const p=new Vector3().fromArray(a.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);expect([p.x,p.y,p.z].every(Number.isFinite)).toBe(true);pts.push(p.x,p.y,p.z);}
   const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(pts,3));const m=new Mesh(g,material);m.name=prim.getMaterial()!.getName();meshes.push(m);
  }
  const t=new Vector3(86.172,0,-28.711).normalize(),normal=new Vector3(t.z,0,-t.x);
  const ray=(height:number)=>new Raycaster(new Vector3(122.486,height,67.458).addScaledVector(t,25).addScaledVector(normal,8),normal.clone().negate(),0,30).intersectObjects(meshes,false);
  expect(ray(14.1).some(h=>h.object.name==='gc_base')).toBe(false);
  expect(ray(14.1).some(h=>h.object.name==='gc_glass'||h.object.name==='gc_door')).toBe(true);
  expect(ray(8).some(h=>h.object.name==='gc_base')).toBe(true);
  const gapU=6.5*Math.hypot(86.172,28.711)/28+2;
  const gapHeight=13.125+1.406*gapU/Math.hypot(86.172,28.711)+.6;
  const gapOrigin=new Vector3(122.486,gapHeight,67.458).addScaledVector(t,gapU).addScaledVector(normal,8);
  expect(new Raycaster(gapOrigin,normal.clone().negate(),0,30).intersectObjects(meshes,false).some(h=>h.object.name==='gc_door')).toBe(true);
 }finally{for(const m of meshes)m.geometry.dispose();material.dispose();}
});
