import { expect,it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Group,Mesh,MeshStandardMaterial,PlaneGeometry,Matrix4,Vector3,BufferGeometry,BufferAttribute,DoubleSide,MeshBasicMaterial,Raycaster } from 'three';
import { loadSurround } from '../src/world/surround';
it('loads the surroundings independently and isolates unavailable assets',async()=>{
 const scene=new Group(),mesh=new Mesh(new PlaneGeometry(6,1),new MeshStandardMaterial());scene.name='street_surround';scene.add(mesh);
 const seating=new Group();for(const name of ['current_left_statue_local_origin','current_right_statue_local_origin']){const c=scene.clone();c.name=name;seating.add(c);}
 expect((await loadSurround(async(url)=>url.endsWith('seating.glb')?seating:scene.clone())).ok).toBe(true);
 const failed=await loadSurround(async()=>{throw Error('unavailable');});expect(failed.ok).toBe(false);expect(failed.root.children).toHaveLength(0);
 expect((await loadSurround(async()=>new Group())).ok).toBe(false);
});
it('preserves the historical source stone, inclined metal rails and shrubs without duplicating the replaced panel',async()=>{
 const root=(await new NodeIO().read('assets/street/hachiko-surround/source/legacy/hachiko-surround-pr88.glb')).getRoot();
 for(const name of ['street_surround','street_surround_stone','street_surround_silver','street_surround_needle','street_surround_panel'])expect(root.listNodes().map(n=>n.getName())).toContain(name);
 const stats=JSON.parse(readFileSync('assets/street/hachiko-surround/source/data/stats.json','utf8'));
 expect(stats.items.find((r:{id:string})=>r.id==='stone-panel')?.replaced_by).toBe('street/hachiko-memorial');
 for(const m of root.listMaterials()){expect(m.getEmissiveFactor()).toEqual([0,0,0]);expect(m.getBaseColorTexture()).toBeNull();if(m.getName().includes('needle'))expect(m.getDoubleSided()).toBe(true);}
});
it('keeps the historical equipment mounting footprint on the sidewalk and new footprints clear of the statue and tactile route',async()=>{
 const io=new NodeIO(),g=(await io.read('assets/ground/core/web/ground_core.glb')).getRoot(),surfaces:Mesh[]=[];
 for(const n of g.listNodes())if(n.getName().startsWith('ground_sidewalk'))for(const p of n.getMesh()?.listPrimitives()??[]){const geo=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));geo.setIndex(new BufferAttribute(p.getIndices()!.getArray()!,1));geo.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));const m=new Mesh(geo,new MeshBasicMaterial({side:DoubleSide}));m.updateMatrixWorld();surfaces.push(m);}
 const stats=JSON.parse(readFileSync('assets/street/hachiko-surround/source/data/stats.json','utf8')),root=(await io.read('assets/street/hachiko-surround/source/legacy/hachiko-surround-pr88.glb')).getRoot(),ray=new Raycaster();let count=0;
 const n=root.listNodes().find(n=>n.getName()==='street_surround_stone')!;
 for(const p of n.getMesh()!.listPrimitives()){const a=p.getAttribute('POSITION')!;for(let i=0;i<a.getCount();i++){const point=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));if(!stats.items.some((r:{anchor_tp:number})=>Math.abs(point.y-r.anchor_tp+15)<.00001))continue;ray.set(new Vector3(point.x,50,point.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(surfaces,false)[0];expect(hit).toBeDefined();expect(point.y-hit.point.y).toBeLessThan(.004);expect(point.y-hit.point.y).toBeGreaterThan(-.12);count++;}}
 expect(count).toBeGreaterThan(30);
 const h=JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json','utf8')),d=stats.config,angle=h.yaw_deg*Math.PI/180;
 const tiles=JSON.parse(readFileSync('assets/street/tactile/source/data/stats.json','utf8')).tiles;
 for(const t of tiles){const dx=t.centre_xy[0]-h.xy[0],dy=t.centre_xy[1]-h.xy[1],x=dx*Math.cos(angle)+dy*Math.sin(angle),y=-dx*Math.sin(angle)+dy*Math.cos(angle);for(const s of d.segments){const distance=Math.hypot(Math.max(s.x0-x,0,x-s.x1),Math.max(d.front_y_m-d.depth_m-y,0,y-d.front_y_m-.16));expect(distance).toBeGreaterThan(.22);}}
 for(const s of d.segments)expect(Math.hypot(Math.max(s.x0,0,-s.x1),Math.max(-d.front_y_m-.16,0))).toBeGreaterThan(.8);
},30000);

it('serves only retained soil and rock plus separate authored replacement assets',async()=>{
 const io=new NodeIO(),base='assets/street/hachiko-surround/';
 const retained=(await io.read(base+'web/hachiko-surround.glb')).getRoot();
 expect(retained.listNodes().filter(n=>n.getMesh()).map(n=>n.getName()).sort()).toEqual(['street_surround_rock','street_surround_soil']);
 const shrubs=(await io.read(base+'web/shrubs.glb')).getRoot();
 const leaves=shrubs.listMaterials().find(m=>m.getAlphaMode()==='MASK')!;
 expect(leaves).toBeDefined();expect(leaves.getDoubleSided()).toBe(true);expect(leaves.getAlphaCutoff()).toBe(.5);
 const seats=(await io.read(base+'web/seating.glb')).getRoot();
 for(const side of ['left','right'])expect(seats.listNodes().some(n=>n.getName()===`current_${side}_statue_local_origin`)).toBe(true);
 for(const [file,tri,prims] of [['shrubs.glb',7224,2],['seating.glb',18824,16]] as const){
  const root=(await io.read(base+'web/'+file)).getRoot();const ps=root.listMeshes().flatMap(m=>m.listPrimitives());
  expect(ps.length).toBe(prims);expect(ps.reduce((n,p)=>n+p.getIndices()!.getCount()/3,0)).toBe(tri);
 }
});
