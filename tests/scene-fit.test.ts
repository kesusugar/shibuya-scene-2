import { describe, expect, it } from 'vitest';
import { Group, Mesh, BoxGeometry, MeshStandardMaterial, Matrix4, Vector3 } from 'three';
import { NodeIO } from '@gltf-transform/core';
import { applySceneFitReplacements, loadSceneFit } from '../src/world/sceneFit';
import { classify } from '../src/world/look';

function part() { const g=new Group(); g.add(new Mesh(new BoxGeometry(),new MeshStandardMaterial())); return g; }

describe('Hachiko local scene fitting', () => {
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
