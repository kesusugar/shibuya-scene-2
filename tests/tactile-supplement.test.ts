import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3,BufferGeometry,Float32BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Raycaster,Group,BoxGeometry} from 'three';
import {loadTactileSupplement} from '../src/world/tactileSupplement';
const json=(p:string)=>JSON.parse(readFileSync(p,'utf8')),io=new NodeIO();
const material=new MeshBasicMaterial({side:DoubleSide});
async function meshes(path:string,filter=(name:string)=>true){const result:Mesh[]=[];for(const n of (await io.read(path)).getRoot().listNodes())if(filter(n.getName()))for(const p of n.getMesh()?.listPrimitives()??[]){const a=p.getAttribute('POSITION')!,idx=p.getIndices()!,world=new Matrix4().fromArray(n.getWorldMatrix()),pts:number[]=[];for(let i=0;i<idx.getCount();i++)pts.push(...new Vector3().fromArray(a.getElement(idx.getScalar(i),[])).applyMatrix4(world).toArray());const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(pts,3));const m=new Mesh(g,material);m.updateMatrixWorld();result.push(m);}return result;}
it('requires each supplement mesh and isolates download failure',async()=>{
 expect((await loadTactileSupplement(async()=>{throw Error('missing')},'extra')).ok).toBe(false);
 const g=new Group(),m=new Mesh(new BoxGeometry(),material);m.name='street_tactile';g.add(m);
 expect((await loadTactileSupplement(async()=>g,'extra')).ok).toBe(true);
 expect((await loadTactileSupplement(async()=>g,'links')).ok).toBe(false);
});
it('drapes both exported supplements to the original sidewalk and connects six modeled open ends',async()=>{
 const ground=await meshes('assets/ground/core/web/ground_core.glb',n=>n.startsWith('ground_sidewalk'));
 const existing=await meshes('assets/street/tactile/web/tactile.glb'),extra=await meshes('assets/street/tactile-extra/web/tactile-extra.glb'),links=await meshes('assets/street/tactile-links/web/tactile-links.glb'),ray=new Raycaster();
 try{
 for(const m of [...extra,...links]){const a=m.geometry.getAttribute('position');for(let i=0;i<a.count;i+=Math.max(1,Math.floor(a.count/160))){const p=new Vector3().fromBufferAttribute(a,i);ray.set(new Vector3(p.x,50,p.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(ground,false)[0];expect(hit).toBeDefined();expect(p.y-hit.point.y).toBeGreaterThan(.0015);expect(p.y-hit.point.y).toBeLessThan(.0075);}}
 const stats=json('assets/street/tactile-links/source/data/stats.json');expect(stats.routes).toHaveLength(6);expect(stats.edge_snaps).toHaveLength(0);expect(stats.overlap_with_prior_tiles_m2).toBeLessThan(1e-6);
 for(const r of stats.routes){expect(r.points).toHaveLength(2);expect(r.endpoint_distance_m).toBeLessThan(1.2);const [a,b]=r.points,l=Math.hypot(b[0]-a[0],b[1]-a[1]),dx=(b[0]-a[0])/l,dy=(b[1]-a[1])/l;
 for(let d=.1;d<l;d+=.2){const hit=[[0,0],[-.006,0],[.006,0],[0,-.006],[0,.006]].some(([along,across])=>{ray.set(new Vector3(a[0]+dx*(d+along)+dy*across,50,-a[1]-dy*(d+along)+dx*across),new Vector3(0,-1,0));return ray.intersectObjects([...existing,...extra,...links],false).length>0;});expect(hit,`${r.id} gap at ${d}m`).toBe(true);}}
 }finally{for(const m of [...ground,...existing,...extra,...links])m.geometry.dispose();}
});
it('closes the rear of both modeled stone planting segments',async()=>{
 const left=await meshes('assets/street/hachiko-surround/web/seating.glb',n=>n==='current_left__stone'),right=await meshes('assets/street/hachiko-surround/web/seating.glb',n=>n==='current_right__stone'),stone=[...left,...right],h=json('assets/street/hachiko/source/data/layout.json'),d=json('assets/street/hachiko-surround/source/data/layout.json'),s=json('assets/street/hachiko-surround/source/data/stats.json');const angle=h.yaw_deg*Math.PI/180;
 const parent=new Matrix4().makeTranslation(h.xy[0],0,-h.xy[1]).multiply(new Matrix4().makeRotationY(angle));
 for(const [list,height] of [[left,.4710693359375],[right,.4155540466308594]] as const)for(const m of list){m.geometry.applyMatrix4(new Matrix4().makeTranslation(0,height,0));m.geometry.applyMatrix4(parent);m.updateMatrixWorld();}
 expect(left.length).toBeGreaterThan(0);expect(right.length).toBeGreaterThan(0);
 try{for(const seg of d.segments){const x=(seg.x0+seg.x1)/2,y=d.front_y_m-d.depth_m-.5,z=s.items.find((i:{id:string})=>i.id===seg.id).anchor_tp-15+.26;const origin=new Vector3(h.xy[0]+x*Math.cos(angle)-y*Math.sin(angle),z,-h.xy[1]-x*Math.sin(angle)-y*Math.cos(angle));const dir=new Vector3(-Math.sin(angle),0,-Math.cos(angle));expect(new Raycaster(origin,dir,0,.8).intersectObjects(stone,false).length).toBeGreaterThan(0);}}
 finally{for(const m of stone)m.geometry.dispose();}
});
