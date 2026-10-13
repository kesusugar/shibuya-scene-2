import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Group, Mesh, MeshStandardMaterial, PlaneGeometry, Vector3, Matrix4, BufferAttribute, BufferGeometry, DoubleSide, MeshBasicMaterial, Raycaster } from 'three';
import { loadHachiko } from '../src/world/hachiko';

it('loads the statue separately and isolates failed or empty supplements', async () => {
  const scene=new Group(),mesh=new Mesh(new PlaneGeometry(1.1,2.4),new MeshStandardMaterial());mesh.name='street_hachiko';scene.add(mesh);
  expect((await loadHachiko(async()=>scene)).ok).toBe(true);expect(mesh.castShadow).toBe(true);
  const missing=await loadHachiko(async()=>{throw new Error('unavailable');});
  expect(missing.ok).toBe(false);expect(missing.root.children).toHaveLength(0);
  expect((await loadHachiko(async()=>new Group())).ok).toBe(false);
});

it('exports the dog, plinth and readable plaque without emissive materials', async () => {
  const root=(await new NodeIO().read('assets/street/hachiko/web/hachiko.glb')).getRoot();
  const names=root.listNodes().map(n=>n.getName());
  for (const name of ['street_hachiko','street_hachiko_dog','street_hachiko_plinth','street_hachiko_plaque_text','street_hachiko_nose','street_hachiko_collar']) expect(names).toContain(name);
  for (const m of root.listMaterials()) expect(m.getEmissiveFactor()).toEqual([0,0,0]);
  expect(root.listTextures().length).toBeGreaterThanOrEqual(3);
});

it('anchors the exported plinth on the original sidewalk without floating and clears tactile tiles', async () => {
  const io=new NodeIO(),g=(await io.read('assets/ground/core/web/ground_core.glb')).getRoot(),surfaces:Mesh[]=[];
  for (const n of g.listNodes()) if(n.getName().startsWith('ground_sidewalk')) for(const p of n.getMesh()?.listPrimitives()??[]) {
    const geo=new BufferGeometry().setAttribute('position',new BufferAttribute(p.getAttribute('POSITION')!.getArray()!,3));geo.setIndex(new BufferAttribute(p.getIndices()!.getArray()!,1));geo.applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix()));
    const m=new Mesh(geo,new MeshBasicMaterial({side:DoubleSide}));m.updateMatrixWorld();surfaces.push(m);
  }
  const root=(await io.read('assets/street/hachiko/web/hachiko.glb')).getRoot(),n=root.listNodes().find(n=>n.getName()==='street_hachiko_foot')!;
  const points=n.getMesh()!.listPrimitives().flatMap(p=>{const a=p.getAttribute('POSITION')!;return Array.from({length:a.getCount()},(_,i)=>new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(new Matrix4().fromArray(n.getWorldMatrix())));});
  const bottom=Math.min(...points.map(p=>p.y)),ray=new Raycaster();let checked=0;
  for (const p of points.filter(p=>p.y<bottom+.009)) {
    ray.set(new Vector3(p.x,50,p.z),new Vector3(0,-1,0));const h=ray.intersectObjects(surfaces,false)[0];expect(h).toBeDefined();
    expect(p.y-h.point.y).toBeLessThan(.012);expect(p.y-h.point.y).toBeGreaterThan(-.15);checked++;
  }
  expect(checked).toBeGreaterThan(8);
  const layout=JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json','utf8'));
  const tiles=JSON.parse(readFileSync('assets/street/tactile/source/data/stats.json','utf8')).tiles;
  for (const t of tiles) expect(Math.hypot(t.centre_xy[0]-layout.xy[0],t.centre_xy[1]-layout.xy[1])).toBeGreaterThan(1.2);
},30000);
