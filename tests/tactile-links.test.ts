import { expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { NodeIO } from '@gltf-transform/core';
import { Matrix4, Vector3 } from 'three';

it('joins both plaza approaches through the junction without guide ribs crossing its warning surface', async () => {
  const root=(await new NodeIO().read('assets/street/tactile/web/tactile.glb')).getRoot();
  const triangles: number[][][]=[];
  for (const n of root.listNodes()) for (const p of n.getMesh()?.listPrimitives()??[]) {
    const positions=p.getAttribute('POSITION')!,indices=p.getIndices()!,matrix=new Matrix4().fromArray(n.getWorldMatrix());
    for (let i=0;i<indices.getCount();i+=3) triangles.push([0,1,2].map(j=>{
      const v=new Vector3().fromArray(positions.getElement(indices.getScalar(i+j),[])).applyMatrix4(matrix);
      return [v.x,-v.z];
    }));
  }
  const stats=JSON.parse(readFileSync('assets/street/tactile/source/data/stats.json','utf8'));
  const result=execFileSync('python3',['-c',`
import json,sys,math
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
D=json.load(sys.stdin);polys=[];ribs=[]
for t in D['triangles']:
 p=Polygon(t)
 if not p.is_valid or p.area<1e-12:continue
 polys.append(p)
 length=max(math.dist(t[i],t[(i+1)%3]) for i in range(3))
 if length>.15 and 2*p.area/length**2<.2:ribs.append(p)
# Buffer bridges only the designed 3 mm tile grout, not missing route segments.
network=unary_union(polys).buffer(.002)
junction=Polygon(D['stats']['junction']['polygon_xy'])
component=next(p for p in (network.geoms if network.geom_type=='MultiPolygon' else [network]) if p.covers(Point(D['stats']['junction']['centre_xy'])))
for route in D['stats']['routes']:
 if route['id'].startswith('plaza-link:'):
  anchor=next(g for g in D['stats']['groups'] if g['id']==route['from'])
  # The approach marker is at the four tiles' grout intersection, not on a tile.
  assert component.distance(Point(anchor['centre_xy']))<.003,route['id']
 else:
  end=route['end_xy'];d=D['stats']['junction']['direction_xy']
  assert component.covers(Point(end[0]-.01*d[0],end[1]-.01*d[1]))
assert sum(p.intersection(junction).area for p in ribs)<1e-5
print('connected routes, clear junction')
`],{input:JSON.stringify({triangles,stats}),encoding:'utf8'});
  expect(result.trim()).toBe('connected routes, clear junction');
},30000);
