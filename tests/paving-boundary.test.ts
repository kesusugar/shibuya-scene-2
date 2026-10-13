import { expect, it } from 'vitest';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3 } from 'three';

it('partitions concave masks in both windings without losing area or changing sloped heights', () => {
  const result = execFileSync('python3', ['-c', `
import sys
sys.path.insert(0,'assets/ground/core/source/blender')
from paving_boundary import partition

def area(p):
 return abs(sum(p[i-1][0]*p[i][1]-p[i][0]*p[i-1][1] for i in range(len(p)))/2)
polygon=[(0,0),(2,0),(2,1),(1,1),(1,2),(0,2)]
triangle=[(x,y,1+2*x-3*y) for x,y in [(-1,-1),(4,-1),(-1,4)]]
for mask in [polygon,polygon[::-1]]:
 pieces=partition(triangle,mask)
 assert abs(sum(area(p) for p,_ in pieces)-12.5)<1e-8
 assert abs(sum(area(p) for p,inside in pieces if inside)-3)<1e-8
 for piece,inside in pieces:
  for x,y,z in piece:assert abs(z-(1+2*x-3*y))<1e-8
  x=sum(p[0] for p in piece)/len(piece);y=sum(p[1] for p in piece)/len(piece)
  expected=(0<x<2 and 0<y<1) or (0<x<1 and 0<y<2)
  assert inside==expected
print('area and height preserved')
`], { encoding: 'utf8' });
  expect(result.trim()).toBe('area and height preserved');
});

it('clips actual paving triangle vertices to the mask instead of selecting crossing faces by centroid', async () => {
  const polygon: number[][] = JSON.parse(readFileSync('assets/ground/core/source/data/plaza_paving_layout.json','utf8')).polygon_xy_m;
  const inside = (x: number,y: number) => {
    let c=false, distance=Infinity;
    for (let i=0;i<polygon.length;i++) {
      const [ax,ay]=polygon[i], [bx,by]=polygon[(i+1)%polygon.length];
      if ((ay>y)!==(by>y) && x<(bx-ax)*(y-ay)/(by-ay)+ax) c=!c;
      const dx=bx-ax,dy=by-ay,t=Math.max(0,Math.min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)));
      distance=Math.min(distance,Math.hypot(x-ax-t*dx,y-ay-t*dy));
    }
    return c || distance<.0001;
  };
  const root=(await new NodeIO().read('assets/ground/core/web/ground_core.glb')).getRoot();
  let count=0;
  for (const n of root.listNodes()) for (const p of n.getMesh()?.listPrimitives()??[]) {
    if (p.getMaterial()!.getName()!=='ground_sidewalk_plaza_pavers') continue;
    const pos=p.getAttribute('POSITION')!,m=new Matrix4().fromArray(n.getWorldMatrix());
    for (let i=0;i<pos.getCount();i++) {
      const v=new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(m);
      expect(inside(v.x,-v.z)).toBe(true);count++;
    }
  }
  expect(count).toBeGreaterThan(1000);
});
