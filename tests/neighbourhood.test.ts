import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {Matrix4,Vector3} from 'three';
const json=(p:string)=>JSON.parse(readFileSync(p,'utf8'));
for(const id of ['center244','quattro','scramble-square','fukuras','station-southeast','plaza-kiosk']) {
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
        if(p.getMaterial()!.getName()===(id==='center244'?'c244_roof':id+'_roof'))roof.push(v);
      }
    }
    // Center244 upper envelope is an explicit photo-derived billboard proxy; low source roofs remain exact.
    for(const f of s.surfaces.filter((f:{kind:string,ring:number[][]})=>f.kind!=='WallSurface' && (id!=='center244' || Math.max(...f.ring.map(p=>p[2]))<=21.635)))for(const p of f.ring)
      expect(roof.some(v=>v.distanceTo(new Vector3(p[0],p[2],-p[1]))<.002)).toBe(true);
    const stats=json(base+'source/data/stats.json');
    if(id==='center244') {
      expect(stats.upper_reinterpreted_indices).toEqual([1,3,4,5,7,14,17,25,26,27,29,32,33]);
      expect(stats.upper_original_visible_mesh_preserved).toBe(false);
      expect(stats.upper_original_hidden_provenance_preserved).toBe(true);
      expect(stats.source_top_tp).toBe(49.843);
    } else expect(stats.glass_panels).toBeGreaterThan(id==='plaza-kiosk'?10:100);
    expect(stats.roof_translation_m).toBe(0);
    if(['scramble-square','fukuras'].includes(id)){expect(stats.missing_pavement_samples).toBe(0);expect(stats.pavement_samples.length).toBeGreaterThan(30);}
  });
}
