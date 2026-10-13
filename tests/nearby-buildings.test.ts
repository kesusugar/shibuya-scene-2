import {expect,it} from 'vitest';
import {readFileSync,readdirSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3} from 'three';
const json=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
for(const id of ['mark-city','shibuya109','takagi','bic-camera','cine-tower','east-mixeduse','hikarie','parco','stream','sakura-stage'])it(`${id} preserves its source roof and does not duplicate the C parent`,async()=>{
 const base=`assets/buildings/${id}/`,source=json(base+'source/data/plateau.json'),root=(await new NodeIO().read(base+`web/${id}.glb`)).getRoot(),roof:Vector3[]=[];
 const context=json('assets/context/core/source/data/context_input.json');expect(context.buildings.some((b:{plateau_id:string})=>b.plateau_id===source.plateau_id)).toBe(false);
 for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){expect(p.getMaterial()!.getBaseColorTexture()).toBeNull();if(p.getMaterial()!.getName()!==id+'_roof')continue;const a=p.getAttribute('POSITION')!,m=new Matrix4().fromArray(n.getWorldMatrix());for(let i=0;i<a.getCount();i++)roof.push(new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m));}
 for(const s of source.surfaces.filter((s:{kind:string})=>s.kind!=='WallSurface'))for(const p of s.ring)expect(roof.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.002),`${id} roof point ${p}`).toBe(true);
 const stats=json(base+'source/data/stats.json');expect(stats.roof_translation_m).toBe(0);expect(stats.glass_panels).toBeGreaterThan(10);expect(source.matching_overlap_ratio).toBeGreaterThan(.5);expect(json(base+'web/viewer.json').groundElevationTP).toBe(15);
});
it('draws the shared Mark City parent once for both OSM names',()=>{
 const c=json('assets/context/core/source/data/context_input.json');for(const id of ['way/54500467','way/87250190'])expect(c.buildings.some((b:{id:string})=>b.id===id)).toBe(false);
 expect(json('assets/buildings/mark-city/source/data/layout.json').source_aliases).toEqual(['way/87250190']);
 const source=json('assets/buildings/mark-city/source/data/plateau.json');const duplicate=readdirSync('assets/buildings').filter(id=>{try{return json(`assets/buildings/${id}/source/data/plateau.json`).plateau_id===source.plateau_id;}catch{return false;}});expect(duplicate).toEqual(['mark-city']);
});
