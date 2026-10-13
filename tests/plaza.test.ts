import { expect, it } from 'vitest';
import { NodeIO } from '@gltf-transform/core';
import { BufferGeometry, BufferAttribute, DoubleSide, Group, Matrix4, Mesh, MeshBasicMaterial, MeshStandardMaterial, PlaneGeometry, Raycaster, Vector3 } from 'three';
import { loadPlaza } from '../src/world/plaza';
import { classify } from '../src/world/look';

it('accepts a plaza surface and isolates unavailable, empty and non-finite geometry', async () => {
  const scene=new Group(),mesh=new Mesh(new PlaneGeometry(3,3),new MeshStandardMaterial());mesh.name='plaza_finish';scene.add(mesh);
  expect((await loadPlaza(async()=>scene)).ok).toBe(true);
  const failed=await loadPlaza(async()=>{throw new Error('unavailable');});
  expect(failed.ok).toBe(false);expect(failed.root.children).toHaveLength(0);
  expect((await loadPlaza(async()=>new Group())).ok).toBe(false);
  mesh.geometry.getAttribute('position').setX(0,NaN);
  expect((await loadPlaza(async()=>scene)).ok).toBe(false);
});
it('uses original self-generated paving and the sidewalk look class', async () => {
  const root=(await new NodeIO().read('assets/street/plaza-finish/web/plaza-finish.glb')).getRoot();
  expect(root.listMaterials()).toHaveLength(1);
  const m=root.listMaterials()[0];expect(m.getEmissiveFactor()).toEqual([0,0,0]);expect(m.getBaseColorTexture()).not.toBeNull();
  expect(classify(new MeshStandardMaterial({name:m.getName()}),'plaza_finish')).toBe('sidewalk');
});
it('keeps exported paving vertices on the original road with documented 1 mm render offset', async () => {
  const io=new NodeIO(),ground=(await io.read('assets/ground/core/web/ground_core.glb')).getRoot(),surfaces: Mesh[]=[];
  for (const n of ground.listNodes()) {
    if (!n.getName().startsWith('ground_sidewalk')) continue;
    for (const p of n.getMesh()?.listPrimitives()??[]) {
      const geometry=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));
      geometry.setIndex(new BufferAttribute(p.getIndices()!.getArray()!,1));geometry.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
      const mesh=new Mesh(geometry,new MeshBasicMaterial({side:DoubleSide}));mesh.updateMatrixWorld();surfaces.push(mesh);
    }
  }
  const root=(await io.read('assets/street/plaza-finish/web/plaza-finish.glb')).getRoot(),ray=new Raycaster();let count=0;
  for (const n of root.listNodes()) for (const p of n.getMesh()?.listPrimitives()??[]) {
    const positions=p.getAttribute('POSITION')!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
    for (let i=0;i<positions.getCount();i+=Math.max(1,Math.floor(positions.getCount()/120))) {
      const point=new Vector3().fromArray(positions.getElement(i,[])).applyMatrix4(matrix);
      ray.set(new Vector3(point.x,50,point.z),new Vector3(0,-1,0));const hit=ray.intersectObjects(surfaces,false)[0];
      expect(hit).toBeDefined();const offset=point.y-hit.point.y;
      expect(offset).toBeGreaterThan(.0009);expect(offset).toBeLessThan(.0011);count++;
    }
  }
  expect(count).toBeGreaterThan(100);
}, 30000);
