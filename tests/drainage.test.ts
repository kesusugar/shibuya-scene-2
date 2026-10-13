import { expect, it } from 'vitest';
import { NodeIO } from '@gltf-transform/core';
import { BufferGeometry, BufferAttribute, DoubleSide, Group, Matrix4, Mesh, MeshBasicMaterial, MeshStandardMaterial, PlaneGeometry, Raycaster, Vector3 } from 'three';
import { loadDrainage } from '../src/world/drainage';
import { classify } from '../src/world/look';

it('accepts a sub-metre cover and isolates unavailable, empty and non-finite geometry', async () => {
  const scene=new Group(),mesh=new Mesh(new PlaneGeometry(.49,.49),new MeshStandardMaterial());mesh.name='street_drainage';scene.add(mesh);
  expect((await loadDrainage(async()=>scene)).ok).toBe(true);
  const failed=await loadDrainage(async()=>{throw new Error('unavailable');});
  expect(failed.ok).toBe(false);expect(failed.root.children).toHaveLength(0);
  expect((await loadDrainage(async()=>new Group())).ok).toBe(false);
  mesh.geometry.getAttribute('position').setX(0,NaN);
  expect((await loadDrainage(async()=>scene)).ok).toBe(false);
});
it('exports a solid textured-by-geometry cover without photographic texture or emission', async () => {
  const root=(await new NodeIO().read('assets/street/drainage/web/drainage.glb')).getRoot();
  expect(root.listMaterials()).toHaveLength(3);
  for (const m of root.listMaterials()) {
    expect(m.getEmissiveFactor()).toEqual([0,0,0]);expect(m.getBaseColorTexture()).toBeNull();
    expect(classify(new MeshStandardMaterial({name:m.getName()}),'street_drainage')).toBe('furniture');
  }
});
it('keeps exported cover vertices on the original road with documented 16–17 mm render offset', async () => {
  const io=new NodeIO(),ground=(await io.read('assets/ground/core/web/ground_core.glb')).getRoot(),surfaces: Mesh[]=[];
  for (const n of ground.listNodes()) {
    if (!n.getName().match(/^ground_(road|intersection)/)) continue;
    for (const p of n.getMesh()?.listPrimitives()??[]) {
      const geometry=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));
      geometry.setIndex(new BufferAttribute(p.getIndices()!.getArray()!,1));geometry.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
      const mesh=new Mesh(geometry,new MeshBasicMaterial({side:DoubleSide}));mesh.updateMatrixWorld();surfaces.push(mesh);
    }
  }
  const root=(await io.read('assets/street/drainage/web/drainage.glb')).getRoot(),ray=new Raycaster();let count=0;
  for (const n of root.listNodes()) for (const p of n.getMesh()?.listPrimitives()??[]) {
    const positions=p.getAttribute('POSITION')!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
    for (let i=0;i<positions.getCount();i+=Math.max(1,Math.floor(positions.getCount()/120))) {
      const point=new Vector3().fromArray(positions.getElement(i,[])).applyMatrix4(matrix);
      ray.set(new Vector3(point.x,50,point.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(surfaces,false)[0];
      expect(hit).toBeDefined();const offset=point.y-hit.point.y;
      expect(offset).toBeGreaterThan(.0159);expect(offset).toBeLessThan(.0171);count++;
    }
  }
  expect(count).toBeGreaterThan(100);
}, 30000);
