import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide, Raycaster } from 'three';
const base = 'assets/buildings/west-block/';
it('replaces the original C shell exactly once and keeps the PLATEAU source and measured ground datum', () => {
 const source=JSON.parse(readFileSync(base+'source/data/plateau.json','utf8'));
 const context=JSON.parse(readFileSync('assets/context/core/source/data/context_input.json','utf8'));
 const stats=JSON.parse(readFileSync(base+'source/data/stats.json','utf8'));
 const hints=JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 expect(source.id).toBe('way/136690966');
 expect(context.buildings.some((b:{id:string})=>b.id===source.id)).toBe(false);
 expect(context.excluded.filter((b:{id:string})=>b.id===source.id)).toHaveLength(1);
 expect(hints.groundElevationTP).toBe(stats.anchor_tp);
 expect(Math.abs(stats.roof_deviation_vs_plateau_m)).toBeLessThan(.2);
});
it('separates dated signs from geometry and preserves colour textures at night', async () => {
 const io=new NodeIO();
 const root=(await io.read(base+'web/signs-2025-01.glb')).getRoot();
 const names=root.listMaterials().map(m=>m.getName());
 for (const name of ['hisamitsu', 'rakuten', 'dmm', 'taiseido_left', 'taiseido_right', 'sanzenri']) {
  expect(names.filter(n => n === 'west_sign_' + name)).toHaveLength(1);
 }
 expect(names).not.toContain('west_sign_taiseido');
 for(const material of root.listMaterials()) {
  expect(material.getBaseColorTexture()).not.toBeNull();
  expect(material.getEmissiveTexture()).not.toBeNull();
 }
 const plain=(await io.read(base+'web/west-block.glb')).getRoot();
 expect(plain.listMaterials().some(m=>m.getName().startsWith('west_sign_'))).toBe(false);
 for(const node of plain.listNodes()) {
  if(!node.getMesh())continue;
  const matrix=new Matrix4().fromArray(node.getWorldMatrix());
  for(const primitive of node.getMesh()!.listPrimitives()) {
   const a=primitive.getAttribute('POSITION')!;
   for(let i=0;i<a.getCount();i++) {
    const p=new Vector3().fromArray(a.getElement(i,[])).applyMatrix4(matrix);
    expect([p.x,p.y,p.z].every(Number.isFinite)).toBe(true);
    expect(p.x).toBeGreaterThan(-70);expect(p.x).toBeLessThan(-30);
    expect(p.y).toBeGreaterThan(-.1);expect(p.y).toBeLessThan(50);
   }
  }
 }
});

// The January revision deliberately separates the inferred exterior/sign envelope
// from the unchanged PLATEAU plan. Do not enlarge planBounds to hide this distinction.
// These are regression constraints, NOT a surveyed footprint or collision clearance.
it('keeps the revised curved and planar signs on their specified surfaces and visible through the shell', async () => {
 const io = new NodeIO();
 const config = JSON.parse(readFileSync(base+'source/data/facades.json','utf8'));
 const hints = JSON.parse(readFileSync(base+'web/viewer.json','utf8'));
 const c = config.corner;
 expect(hints.planBounds).toEqual([-67.253, 21.279, -34.818, 55.545]);
 // Pin the reviewed envelope so changing config and GLBs together cannot silently
 // expand this exception. A future geometry revision must explicitly review it.
 expect(c.center_m).toEqual([-41.53, 32.93]);
 expect(c.radius_m).toBe(8);
 expect(c.center_angle_rad).toBe(-.615);
 expect(c.width_scale).toBe(1.425);
 expect(c.facet_apex_angle_rad).toBe(-.8);
 expect(c.screen_centers_m).toEqual({rakuten:17.9, dmm:8, taiseido:3});
 expect(c.rakuten_height_m).toBe(9.2);
 expect(c.dmm_height_m).toBe(6.7);
 const datum = hints.groundElevationTP - 15;
 const onArc = (angle:number, radius:number, y=0) => new Vector3(
  c.center_m[0]+radius*Math.cos(angle), y+datum, -c.center_m[1]-radius*Math.sin(angle));
 const half = 8*c.width_scale/(2*c.radius_m);
 const left = onArc(c.center_angle_rad-half,c.radius_m+.12);
 const hinge = onArc(c.facet_apex_angle_rad,c.radius_m+.65);
 const right = onArc(c.center_angle_rad+half,c.radius_m+.12);
 const surfaces = [
  {name:'rakuten', y:17.9, height:9.2, a:null, b:null, triangles:48},
  {name:'dmm', y:8, height:6.7, a:hinge, b:right, triangles:2},
  {name:'taiseido_left', y:3, height:1.6, a:left, b:hinge, triangles:2},
  {name:'taiseido_right', y:3, height:1.6, a:hinge, b:right, triangles:2},
 ];
 const material = new MeshBasicMaterial({side:DoubleSide});
 const meshes:Mesh[] = [];
 const seen = new Map<string, Vector3[]>();
 let wholeEast = -Infinity;
 try {
  for (const file of ['west-block.glb','signs-2025-01.glb']) {
   const root = (await io.read(base+'web/'+file)).getRoot();
   for (const node of root.listNodes()) {
    const world = new Matrix4().fromArray(node.getWorldMatrix());
    for (const prim of node.getMesh()?.listPrimitives()??[]) {
     const name = prim.getMaterial()!.getName();
     const pos = prim.getAttribute('POSITION')!, idx = prim.getIndices();
     const vertices:number[] = [];
     for (let i=0; i<(idx?.getCount()??pos.getCount()); i++) {
      const v = new Vector3().fromArray(pos.getElement(idx?idx.getScalar(i):i,[])).applyMatrix4(world);
      v.y += datum;
      vertices.push(v.x,v.y,v.z);
      wholeEast = Math.max(wholeEast,v.x);
      if (surfaces.some(s => name === 'west_sign_'+s.name)) {
       const points = seen.get(name)??[]; points.push(v); seen.set(name,points);
      }
     }
     const geometry = new BufferGeometry();
     geometry.setAttribute('position',new Float32BufferAttribute(vertices,3));
     const mesh = new Mesh(geometry,material); mesh.name = name; meshes.push(mesh);
    }
   }
  }
  // Full-asset east extent is 2.282516m beyond PLATEAU. The photo-aligned ground
  // canopy removes the prior eastmost radial vertex (-32.510506 at z=1.93m),
  // shrinking the envelope by 24.978mm. Unchanged rooftop metal is now eastmost.
  // Keep a millimetre-scale regression guard, not a broad allowance for any sign.
  expect(wholeEast).toBeCloseTo(-32.535484,3);
  for (const s of surfaces) {
   const points = seen.get('west_sign_'+s.name)!;
   expect(points, s.name+' missing').toBeDefined();
   expect(points).toHaveLength(s.triangles*3);
   for (const p of points) {
    expect(Math.abs(Math.abs(p.y-datum-s.y)-s.height/2), s.name+' height').toBeLessThan(.002);
    if (s.a && s.b) {
     // Each planar rectangle must have exactly its four analytic corners.
     const flat = new Vector3(p.x,datum,p.z);
     expect(Math.min(flat.distanceTo(s.a),flat.distanceTo(s.b)), s.name+' facet endpoints').toBeLessThan(.002);
    } else {
     const dx=p.x-c.center_m[0], dy=-p.z-c.center_m[1];
     expect(Math.abs(Math.hypot(dx,dy)-(c.radius_m+.1)), 'Rakuten radius').toBeLessThan(.002);
     const angle=Math.atan2(dy,dx), width=7.7*c.width_scale;
     expect(Math.abs(angle-c.center_angle_rad)).toBeLessThanOrEqual(width/(2*(c.radius_m+.1))+.0001);
    }
   }
   // Independent fixed east bounds make the actual overhang explicit, including
   // both Taiseido faces that the old single-material check did not cover.
   const east = Math.max(...points.map(p=>p.x));
   const expectedEast = s.name==='rakuten' ? -33.430141 : s.name==='taiseido_left' ? -35.503487 : -33.448566;
   expect(east).toBeCloseTo(expectedEast,3);
  }
  const cam = JSON.parse(readFileSync('assets/street/core/web/projected.json','utf8')).camera.pos;
  const origin = new Vector3(cam[0],cam[2],-cam[1]);
  // Nine interior probes per surface, not just one old cylindrical target. Cast
  // against ALL base and sign meshes so the old shell or an opaque cover fails.
  for (const s of surfaces) for (const u of [.2,.5,.8]) for (const v of [.25,.5,.75]) {
   const y=s.y+(v-.5)*s.height;
   const target = s.a && s.b ? s.a.clone().lerp(s.b,u) : onArc(
    c.center_angle_rad+(u-.5)*7.7*c.width_scale/(c.radius_m+.1),c.radius_m+.1);
   target.y=y+datum;
   const ray = new Raycaster(origin,target.clone().sub(origin).normalize());
   const first = ray.intersectObjects(meshes,false)[0];
   expect(first?.object.name, s.name+' hidden at '+u+','+v).toBe('west_sign_'+s.name);
   expect(first.point.distanceTo(target), s.name+' ray hits a displaced surface').toBeLessThan(.01);
  }
 } finally {for (const mesh of meshes) mesh.geometry.dispose(); material.dispose();}
});
