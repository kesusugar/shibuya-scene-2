import { describe, expect, it } from 'vitest';
import { Group, Mesh, BoxGeometry, MeshStandardMaterial, Matrix4, Vector3, BufferGeometry, Float32BufferAttribute, Raycaster, DoubleSide } from 'three';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { applySceneFitReplacements, loadSceneFit } from '../src/world/sceneFit';
import { classify } from '../src/world/look';

function part() { const g=new Group(); g.add(new Mesh(new BoxGeometry(),new MeshStandardMaterial())); return g; }

// Actual shipped geometry, including node transforms, for contact and clearance tests.
async function geometry(file:string, keep=(name:string)=>true) {
  const group=new Group(), root=(await new NodeIO().read(file)).getRoot();
  for(const node of root.listNodes().filter(n=>keep(n.getName()))) for(const prim of node.getMesh()?.listPrimitives()??[]) {
    const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(prim.getAttribute('POSITION')!.getArray()!,3));
    if(prim.getIndices()) g.setIndex(Array.from(prim.getIndices()!.getArray()!));
    g.applyMatrix4(new Matrix4().fromArray(node.getWorldMatrix()));
    group.add(new Mesh(g,new MeshStandardMaterial({side:DoubleSide})));
  }
  group.updateMatrixWorld(true);return group;
}

describe('Hachiko local scene fitting', () => {
  it('has a continuous roof across the locally replaced A8 canopy',async()=>{
    const roof=await geometry('assets/street/hachiko-fit/web/a8.glb');
    const a=8.3*Math.PI/180,co=Math.cos(a),si=Math.sin(a);
    for(const u of [-2.8,-1.4,0,1.4,2.8]) for(const v of [-4.3,-2,0,2,4.4]) {
      const ray=new Raycaster(new Vector3(35.25+co*u-si*v,8,-(-47+si*u+co*v)),new Vector3(0,-1,0));
      const hit=ray.intersectObject(roof,true)[0];expect(hit,`${u},${v}`).toBeDefined();expect(hit.point.y).toBeGreaterThanOrEqual(4.039);
    }
  });
  it('connects the actual last guidance tile with a tangent continuation clear of existing walls',async()=>{
    const route=JSON.parse(readFileSync('assets/street/hachiko-fit/web/tactile.json','utf8'));
    const old=JSON.parse(readFileSync('assets/street/tactile/source/data/stats.json','utf8')).tiles.filter((t:any)=>t.group==='plaza-south-continuation').at(-1);
    const points:number[][]=route.route_points_xy_m;
    for(let i=0;i<2;i++) expect(points[0][i]).toBeCloseTo(old.centre_xy[i]+old.direction_xy[i]*.15,5);
    const first=new Vector3(points[1][0]-points[0][0],0,points[1][1]-points[0][1]).normalize();
    expect(first.x).toBeCloseTo(old.direction_xy[0],5);expect(first.z).toBeCloseTo(old.direction_xy[1],5);
    const ground=await geometry('assets/ground/core/web/ground_core.glb',n=>/^ground_(sidewalk|island|fill)/.test(n));
    const obstacles=await Promise.all(['assets/buildings/plaza-kiosk/web/plaza-kiosk.glb','assets/buildings/shibu-hachi-box/web/shibu-hachi-box.glb','assets/buildings/station-north/web/station-north.glb','assets/street/hachiko-fit/web/a8.glb','assets/street/hachiko-fit/web/kerb.glb'].map(f=>geometry(f)));
    for(let i=0;i<points.length-1;i++) {
      const from=new Vector3(points[i][0],0,-points[i][1]),to=new Vector3(points[i+1][0],0,-points[i+1][1]);
      const length=from.distanceTo(to),dir=to.clone().sub(from).normalize();
      for(let d=0;d<length;d+=.3) {
        const p=from.clone().addScaledVector(dir,d);const down=new Raycaster(p.clone().setY(30),new Vector3(0,-1,0));
        const hit=down.intersectObject(ground,true)[0];expect(hit).toBeDefined();
        for(const h of [.25,.5,1.3]) {
          const ray=new Raycaster(p.clone().setY(hit.point.y+h),dir,0,Math.min(.3,length-d)+.4);
          expect(ray.intersectObjects(obstacles,true),`segment ${i} distance ${d.toFixed(2)} height ${h}`).toHaveLength(0);
        }
      }
    }
  });
  it('closes the wall around the retained trunk in every direction',async()=>{
    const wall=await geometry('assets/street/hachiko-fit/web/enclosure.glb',n=>n.endsWith('enclosure_stone'));
    const ground=await geometry('assets/ground/core/web/ground_core.glb',n=>/^ground_(sidewalk|island|fill)/.test(n));
    const p=new Vector3(7.4,30,45.5);const down=new Raycaster(p,new Vector3(0,-1,0));
    p.y=down.intersectObject(ground,true)[0].point.y+.25;
    for(let i=0;i<32;i++) {
      const a=i*Math.PI/16,ray=new Raycaster(p,new Vector3(Math.cos(a),0,Math.sin(a)),0,4);
      expect(ray.intersectObject(wall,true).length,`direction ${i}`).toBeGreaterThan(0);
    }
  });
  it('classifies the actual fitted lottery lettering and glazing separately from the shell', async () => {
    const root=(await new NodeIO().read('assets/street/hachiko-fit/web/lottery.glb')).getRoot();
    const classes=new Set<string>();
    for(const node of root.listNodes().filter(n=>n.getName().startsWith('A28_'))) {
      for(const prim of node.getMesh()?.listPrimitives()??[]) classes.add(classify(new MeshStandardMaterial({name:prim.getMaterial()!.getName()}),node.getName()));
    }
    expect([...classes].sort()).toEqual(['furniture','glass','sign']);
  });
  it('accepts the bounded small fence detail without lowering the other assets size check', async () => {
    const detail=new Group();detail.add(new Mesh(new BoxGeometry(.57,.44,.16),new MeshStandardMaterial()));
    expect((await loadSceneFit(async()=>detail,['fence'])).ok).toBe(true);
    expect((await loadSceneFit(async()=>detail,['a8'])).ok).toBe(false);
  });
  it('replaces only selected visible roots and preserves originals on load failure', async () => {
    const originals={facilities:part(),plaza:part(),kiosk:part()};
    const geometry=(originals.facilities.children[0] as Mesh).geometry;
    const normal=await loadSceneFit(async()=>part(),['lottery','enclosure','finish']);
    applySceneFitReplacements(normal,originals);
    expect(originals.facilities.visible).toBe(false); expect(originals.plaza.visible).toBe(false);
    expect(originals.kiosk.visible).toBe(true);
    expect((originals.facilities.children[0] as Mesh).geometry).toBe(geometry);
    const failed=await loadSceneFit(async()=>{throw Error('missing fitted asset');},['a8']);
    applySceneFitReplacements(failed,originals);
    expect(failed.ok).toBe(false); expect(failed.root.children).toHaveLength(0);
    expect(originals.kiosk.visible).toBe(true);
  });

  it('keeps every local paving vertex at its original position and elevation', async () => {
    const io=new NodeIO();
    async function positions(file:string) {
      const root=(await io.read(file)).getRoot(); const result:string[]=[];
      for(const node of root.listNodes()) for(const prim of node.getMesh()?.listPrimitives()??[]) {
        const p=prim.getAttribute('POSITION')!; const matrix=new Matrix4().fromArray(node.getWorldMatrix());
        for(let i=0;i<p.getCount();i++) {const v=new Vector3().fromArray(p.getElement(i,[])).applyMatrix4(matrix); result.push(v.toArray().map(n=>n.toFixed(4)).join(','));}
      }
      // UV seams can duplicate accessor vertices on re-export; compare their world positions.
      return [...new Set(result)].sort();
    }
    expect(await positions('assets/street/hachiko-fit/web/finish.glb')).toEqual(await positions('assets/street/plaza-finish/web/plaza-finish.glb'));
  });

  it('retains northern kiosk roof vertices in the A8 partial replacement', async () => {
    const io=new NodeIO(); const old=(await io.read('assets/buildings/plaza-kiosk/web/plaza-kiosk.glb')).getRoot();
    const fitted=(await io.read('assets/street/hachiko-fit/web/a8.glb')).getRoot();
    const north=(r:typeof old) => r.listNodes().filter(n=>n.getName().startsWith('plaza-kiosk_roof')).flatMap(n=>n.getMesh()!.listPrimitives().flatMap(p=>{
      const pos=p.getAttribute('POSITION')!;const vertices:string[]=[];
      for(let i=0;i<pos.getCount();i++){const v:number[]=pos.getElement(i,[] as number[]);if(v[2]<40)vertices.push(v.map(x=>x.toFixed(3)).join(','));}
      return [...new Set(vertices)].sort();
    }));
    expect(north(fitted)).toEqual(expect.arrayContaining(north(old))); expect(north(old).length).toBeGreaterThan(0);
  });
});
