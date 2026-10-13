import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { BufferGeometry, BufferAttribute, DoubleSide, Group, Matrix4, Mesh, MeshBasicMaterial, MeshStandardMaterial, PlaneGeometry, Raycaster, Vector3 } from 'three';
import { loadTactile } from '../src/world/tactile';
import { classify } from '../src/world/look';

it('loads tactile geometry independently and reports a failed supplement without a placeholder', async () => {
  const scene=new Group(),mesh=new Mesh(new PlaneGeometry(3,.3),new MeshStandardMaterial());mesh.name='street_tactile';scene.add(mesh);
  const ok=await loadTactile(async()=>scene);
  expect(ok.ok).toBe(true);expect(ok.stats.meshes).toBe(1);expect(ok.stats.triangles).toBe(2);
  expect(mesh.castShadow).toBe(false);
  const fail=await loadTactile(async()=>{throw new Error('unavailable');});
  expect(fail.ok).toBe(false);expect(fail.root.children).toHaveLength(0);expect(fail.error).toContain('unavailable');
});

it('exports yellow unlit-by-emission tactile surfaces in the furniture class', async () => {
  const root=(await new NodeIO().read('assets/street/tactile/web/tactile.glb')).getRoot();
  const m=root.listMaterials()[0];
  expect(m.getEmissiveFactor()).toEqual([0,0,0]);expect(m.getBaseColorTexture()).toBeNull();expect(m.getRoughnessFactor()).toBeCloseTo(.9,6);
  expect(classify(new MeshStandardMaterial({name:m.getName()}),'street_tactile')).toBe('furniture');
  const r=m.getBaseColorFactor();expect(r[0]).toBeGreaterThan(r[1]);expect(r[1]).toBeGreaterThan(r[2]*10);
});

it('keeps exported tactile vertices on the existing sidewalk with 2–7 mm relief', async () => {
  const io=new NodeIO(),ground=(await io.read('assets/ground/core/web/ground_core.glb')).getRoot(),surfaces: Mesh[]=[];
  for (const n of ground.listNodes()) {
    if (!n.getName().startsWith('ground_sidewalk')) continue;
    for (const p of n.getMesh()?.listPrimitives()??[]) {
      const geometry=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));
      geometry.setIndex(new BufferAttribute(p.getIndices()!.getArray()!,1));geometry.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
      const mesh=new Mesh(geometry,new MeshBasicMaterial({side:DoubleSide}));mesh.updateMatrixWorld();surfaces.push(mesh);
    }
  }
  const root=(await io.read('assets/street/tactile/web/tactile.glb')).getRoot(),ray=new Raycaster();let count=0;
  for (const n of root.listNodes()) for (const p of n.getMesh()?.listPrimitives()??[]) {
    const positions=p.getAttribute('POSITION')!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
    for (let i=0;i<positions.getCount();i+=Math.max(1,Math.floor(positions.getCount()/120))) {
      const point=new Vector3().fromArray(positions.getElement(i,[])).applyMatrix4(matrix);
      ray.set(new Vector3(point.x,50,point.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(surfaces,false)[0];
      expect(hit).toBeDefined();const offset=point.y-hit.point.y;
      expect(offset).toBeGreaterThan(.0019);expect(offset).toBeLessThan(.0071);count++;
    }
  }
  expect(count).toBeGreaterThan(100);
  const stats=JSON.parse(readFileSync('assets/street/tactile/source/data/stats.json','utf8'));
  expect(stats.groups.filter((g: {status:string})=>g.status==='prototype')).toHaveLength(6);
}, 30000);

it('keeps warning and guide footprints clear of existing pole bases', () => {
  const tiles=JSON.parse(readFileSync('assets/street/tactile/source/data/stats.json','utf8')).tiles;
  const poles=JSON.parse(readFileSync('assets/street/core/source/data/street_layout.json','utf8')).items;
  for (const t of tiles) for (const p of poles) {
    if (!p.xy) continue;
    const [dx,dy]=[p.xy[0]-t.centre_xy[0],p.xy[1]-t.centre_xy[1]],d=t.direction_xy;
    const across=Math.abs(dx*d[1]-dy*d[0]),along=Math.abs(dx*d[0]+dy*d[1]);
    expect(Math.hypot(Math.max(across-.15,0),Math.max(along-.15,0))).toBeGreaterThanOrEqual(.1999);
  }
});
