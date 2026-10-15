import { expect, it } from 'vitest';
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Raycaster, Vector3, InstancedMesh } from 'three';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { loadProps, type PropLayout } from '../src/world/props';
import { classify } from '../src/world/look';
const asset=()=>{const g=new Group();g.add(new Mesh(new BoxGeometry(.2,1,.4),new MeshStandardMaterial({color:0xffffff})));return g;};
const row={id:'one',prop:'post',xy:[3,4] as [number,number],yaw_deg:90,basis:'dated photo, inferred coordinates',source_photo:'ref.jpg',observed_date:'2025-10-10',status:'estimated' as const};
const layout:PropLayout={props:{post:{file:'post.glb',size_m:[.2,.4,1]}},placements:[row]};
const json=(x:PropLayout)=>async<T>()=>x as T;
it('grounds rotated feet, keeps canonical scale and participates in real ray collisions',async()=>{
 const r=await loadProps(async()=>asset(),json(layout),(x)=>2+x*.01);
 expect(r.ok).toBe(true);expect(r.stats.placed).toBe(1);expect(r.anchors[0].ground).toBeCloseTo(2.032,5);
 expect(r.anchors[0].baseGap).toBeCloseTo(.004,5);
 r.root.updateMatrixWorld(true);
 const ray=new Raycaster(new Vector3(2,2.5,-4),new Vector3(1,0,0),0,2);
 expect(ray.intersectObject(r.root,true)[0].distance).toBeCloseTo(.8,5);
 const m=r.root.children[0].children[0] as InstancedMesh;
 expect(classify(m.material as MeshStandardMaterial,m.name)).toBe('furniture');
});
it('does not float over a hole or straddle a large step',async()=>{
 for(const ground of [(x:number)=>x>3?null:0,(x:number)=>x>3?.3:0]){
  const r=await loadProps(async()=>asset(),json(layout),ground);
  expect(r.ok).toBe(false);expect(r.stats.placed).toBe(0);expect(r.stats.skipped).toBe(1);expect(r.root.children).toHaveLength(0);
 }
});
it('keeps a valid prop when another model fails to load',async()=>{
 const mixed:PropLayout={props:{...layout.props,bad:{file:'bad.glb',size_m:[.2,.4,1]}},placements:[row,{...row,id:'two',prop:'bad'}]};
 const r=await loadProps(async url=>{if(url.endsWith('bad.glb'))throw new Error('HTTP 404');return asset();},json(mixed),()=>0);
 expect(r.ok).toBe(false);expect(r.stats.placed).toBe(1);expect(r.stats.skipped).toBe(1);expect(r.root.children).toHaveLength(1);
});
it('rejects a unit mismatch instead of silently rescaling the original asset',async()=>{
 const r=await loadProps(async()=>{const a=asset();a.scale.setScalar(100);return a;},json(layout),()=>0);
 expect(r.ok).toBe(false);expect(r.stats.placed).toBe(0);expect(r.errors[0]).toContain('dimensions');
});
it('shares instanced geometry but keeps all repeated objects collidable',async()=>{
 const r=await loadProps(async()=>asset(),json({...layout,placements:[row,{...row,id:'two',xy:[6,4]}]}),()=>0);
 expect(r.stats.draws).toBe(1);expect(r.stats.triangles).toBe(24);r.root.updateMatrixWorld(true);
 for(const x of [3,6])expect(new Raycaster(new Vector3(x-1,.5,-4),new Vector3(1,0,0),0,2).intersectObject(r.root,true)).not.toHaveLength(0);
});
it('ships the dots models unchanged and records evidence for every normal placement',()=>{
 const l=JSON.parse(readFileSync('assets/street/props/web/layout.json','utf8')) as PropLayout;
 expect(l.placements).toHaveLength(6);expect(new Set(l.placements.map(p=>p.id)).size).toBe(6);
 for(const [id,p]of Object.entries(l.props)){
  const hash=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
  expect(hash(`assets/street/props/web/${p.file}`)).toBe(hash(`assets/street/props/incoming/${id}/${p.file}`));
 }
 for(const p of l.placements){expect(readFileSync(p.source_photo).byteLength).toBeGreaterThan(100);expect(p.status).toBe('estimated');}
 expect(Object.keys(l.props)).not.toContain('green_railing_upper_panel');expect(Object.keys(l.props)).not.toContain('grey_louvered_cabinet');
});
