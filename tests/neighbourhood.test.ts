import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3} from 'three';
const json=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
for(const id of ['center244','quattro','scramble-square','fukuras']) {
  it(`${id} replaces C once and retains surveyed roof coordinates`,async()=>{
    const base=`assets/buildings/${id}/`,s=json(base+'source/data/plateau.json');
    for(const name of ['context_input','context_stats']) {
      const c=json(`assets/context/core/source/data/${name}.json`);
      expect(c.buildings.some((b:{id:string})=>b.id===s.id)).toBe(false);
      expect(c.excluded.filter((b:{id:string})=>b.id===s.id)).toHaveLength(1);
    }
    const root=(await new NodeIO().read(base+`web/${id}.glb`)).getRoot(),roof:Vector3[]=[];
    for(const n of root.listNodes()) for(const p of n.getMesh()?.listPrimitives()??[]) {
      expect(p.getMaterial()!.getBaseColorTexture()).toBeNull();
      const a=p.getAttribute('POSITION')!,m=new Matrix4().fromArray(n.getWorldMatrix());
      for(let i=0;i<a.getCount();i++) {
        const v=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(m);
        expect([v.x,v.y,v.z].every(Number.isFinite)).toBe(true);
        if(p.getMaterial()!.getName()===id+'_roof')roof.push(v);
      }
    }
    for(const f of s.surfaces.filter((f:{kind:string})=>f.kind!=='WallSurface'))for(const p of f.ring)
      expect(roof.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.002)).toBe(true);
    const stats=json(base+'source/data/stats.json');
    expect(stats.glass_panels).toBeGreaterThan(100);
    expect(stats.roof_translation_m).toBe(0);
    if(['scramble-square','fukuras'].includes(id))expect(stats.missing_pavement_samples).toBeGreaterThan(0);
  });
}
