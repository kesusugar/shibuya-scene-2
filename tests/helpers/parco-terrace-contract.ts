import { strict as assert } from 'node:assert';
import { Matrix4, Quaternion, ShapeUtils, Vector2, Vector3 } from 'three';

export type P2 = [number, number];
export type P3 = [number, number, number];
export type Triangle = { owner: string; slot: number; points: [P3, P3, P3]; e1: P3; e2: P3 };
export const WALL_CUTS = [52, 128, 195, 273, 372, 373, 451];
export const SPANDREL_CUTS = [84, 85, 108, 109, 201, 202, 225, 226];
export const TERRACE_NAMES = ['structure', 'floor', 'glass', 'frame', 'rail', 'retained', 'retained_spandrel'].map(s => `prototype_terrace_${s}`);
export const ZONES = [
  { face: 171, a: [-110.668, 276.864] as P2, b: [-119.881, 294.839] as P2, rects: [[0, 20.198614648359683, 25.3779, 34.7]] },
  { face: 108, a: [-118.839, 295.526] as P2, b: [-125.516, 307.472] as P2, rects: [[0, 13.685466089367115, 26.2, 39.3]] },
  { face: 152, a: [-125.516, 307.472] as P2, b: [-144.222, 306.519] as P2, rects: [[0, 11, 26.2, 39.3], [11, 18.730360142347198, 30.178, 39.3]] },
];
// Review-contract coordinates, not loaded from mutable production reports/config.
// They are inferred model coordinates, not a survey or as-built tolerance claim.
export const POLYGONS: Record<string, P2[]> = {
  east: [[-110.668,276.864],[-119.881,294.839],[-124.47631424842488,294.7639077674637],[-139.26616727530927,290.10325250065364],[-137.59178371649233,284.7898608576619],[-125.04779726035706,288.7427869913637],[-122.07994324344486,272.6366709137836]],
  corner: [[-119.881,294.839],[-118.839,295.526],[-125.516,307.472],[-144.222,306.519],[-145.96532215708874,299.1322927706454],[-139.26616727530927,290.10325250065364],[-124.47631424842488,294.7639077674637]],
  north: [[-144.222,306.519],[-136.50175238337368,306.9123174371135],[-135.33853887110516,302.4810598882793],[-145.96532215708874,299.1322927706454]],
  core: [[-142.45957921738284,300.23704068574114],[-133.58566740125218,303.0334338458271],[-133.91363943854623,304.07420128105235],[-127.99769822779247,305.9384633877764],[-124.47631424842488,294.7639077674637],[-139.26616727530927,290.10325250065364]],
};
export const RETURNS: P2[][] = [
  [[-144.222,306.519],[-145.96532215708874,299.1322927706454]],
  [[-145.96532215708874,299.1322927706454],[-142.45957921738284,300.23704068574114]],
];
const sizes: Record<number, number> = {5121: 1, 5123: 2, 5125: 4, 5126: 4};
const counts: Record<string, number> = {SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4};
export function parseGLB(bytes: Buffer) {
  assert.equal(bytes.toString('ascii',0,4),'glTF'); assert.equal(bytes.readUInt32LE(4),2);
  assert.equal(bytes.readUInt32LE(8),bytes.length); assert.equal(bytes.readUInt32LE(16),0x4e4f534a);
  const jsonEnd=20+bytes.readUInt32LE(12), binStart=jsonEnd+8;
  assert.equal(bytes.readUInt32LE(jsonEnd+4),0x004e4942);
  assert.equal(binStart+bytes.readUInt32LE(jsonEnd),bytes.length);
  const document=JSON.parse(bytes.subarray(20,jsonEnd).toString('utf8'));
  const range=(id:number,element:number) => {
    const a=document.accessors[id],v=document.bufferViews[a.bufferView];
    assert.equal(a.sparse,undefined); assert.equal(v.buffer??0,0); assert(element>=0&&element<a.count);
    const length=sizes[a.componentType]*counts[a.type]; assert(Number.isFinite(length));
    const offset=binStart+(v.byteOffset??0)+(a.byteOffset??0)+element*(v.byteStride??length);
    assert(offset>=binStart&&offset+length<=bytes.length); return {offset,length};
  };
  const scalar=(id:number,element:number) => {
    const {offset}=range(id,element),type=document.accessors[id].componentType;
    if(type===5121)return bytes.readUInt8(offset);
    if(type===5123)return bytes.readUInt16LE(offset);
    if(type===5125)return bytes.readUInt32LE(offset);
    throw Error(`unsupported index type ${type}`);
  };
  const vec3=(id:number,element:number):P3 => {
    assert.equal(document.accessors[id].componentType,5126);assert.equal(document.accessors[id].type,'VEC3');
    const {offset}=range(id,element);return [bytes.readFloatLE(offset),bytes.readFloatLE(offset+4),bytes.readFloatLE(offset+8)];
  };
  const triangle=(id:number,slot:number) => [0,1,2].map(k=>scalar(id,slot*3+k));
  return {bytes,document,binStart,range,scalar,vec3,triangle};
}
export type GLB=ReturnType<typeof parseGLB>;
export function encodeGLB(document:any, binary:Buffer) {
  let j=Buffer.from(JSON.stringify(document));j=Buffer.concat([j,Buffer.alloc((4-j.length%4)%4,32)]);
  const b=Buffer.concat([binary,Buffer.alloc((4-binary.length%4)%4)]),out=Buffer.alloc(28+j.length+b.length);
  out.write('glTF');out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);out.writeUInt32LE(j.length,12);out.writeUInt32LE(0x4e4f534a,16);j.copy(out,20);
  out.writeUInt32LE(b.length,20+j.length);out.writeUInt32LE(0x004e4942,24+j.length);b.copy(out,28+j.length);return out;
}
export function replaceTriangle(g:GLB,mesh:number,slot:number,indices:number[]) {
  const id=g.document.meshes[mesh].primitives[0].indices;
  assert.equal(g.document.accessors[id].componentType,5123);
  indices.forEach((v,k)=>g.bytes.writeUInt16LE(v,g.range(id,slot*3+k).offset));
}
export function assertPreservation(prior:GLB,current:GLB,components:any[]) {
  const a=prior.document,b=current.document;
  for(const key of ['nodes','meshes','materials','accessors','bufferViews'])assert.deepEqual(b[key].slice(0,a[key].length),a[key],`original ${key}`);
  for(const key of ['images','textures','samplers'])assert.deepEqual(b[key]??[],a[key]??[],`original ${key}`);
  assert.deepEqual(b.scenes[b.scene??0].nodes.slice(0,a.nodes.length),a.scenes[a.scene??0].nodes,'original scene membership');
  assert.equal(a.meshes.length,12);assert.equal(b.meshes.length,19);assert.equal(b.nodes.length,19);
  assert.deepEqual(b.meshes.slice(12).map((m:any)=>m.name),TERRACE_NAMES);
  const allowed:Record<number,Set<number>>={1:new Set(WALL_CUTS),7:new Set(SPANDREL_CUTS)};
  for(const [mesh,material] of [[8,'cladding'],[9,'joint'],[10,'glass'],[11,'rail_glass']] as const) {
    const owned=components.filter(c=>c.material===material);
    assert.equal(owned.length*12,a.accessors[a.meshes[mesh].primitives[0].indices].count/3);
    allowed[mesh]=new Set(owned.flatMap((c,i)=>['pale_cladding_panel','reveal_backing'].includes(c.kind)?[]:Array.from({length:12},(_,j)=>12*i+j)));
  }
  // Reconstruct the whole original BIN prefix. Only enumerated triangles become
  // explicit degenerates; this catches normals, roof22, padding and all other bytes.
  const expected=Buffer.from(prior.bytes.subarray(prior.binStart));
  for(const [mesh,slots] of Object.entries(allowed)) {
    const p=a.meshes[Number(mesh)].primitives[0];assert.equal(a.accessors[p.indices].componentType,5123);
    for(const slot of slots) {
      const original=prior.triangle(p.indices,slot);assert(new Set(original).size===3);
      // Old shallow prism groups collapse to the first vertex of the entire
      // 12-triangle component; wall/spandrel cuts use their own first vertex.
      const anchor=Number(mesh)>=8?prior.triangle(p.indices,Math.floor(slot/12)*12)[0]:original[0];
      for(let k=0;k<3;k++)expected.writeUInt16LE(anchor,prior.range(p.indices,slot*3+k).offset-prior.binStart);
      assert.deepEqual(current.triangle(p.indices,slot),[anchor,anchor,anchor],`authorized placeholder ${mesh}/${slot}`);
    }
  }
  assert(current.bytes.subarray(current.binStart,current.binStart+expected.length).equals(expected),'unapproved original binary edit, including roof22/source108/152');
  // Separate exact whole-roof proof is intentionally redundant and diagnostic.
  const roof=a.meshes[0].primitives[0];
  for(const id of [roof.indices,...Object.values(roof.attributes)] as number[])for(let i=0;i<a.accessors[id].count;i++) {
    const x=prior.range(id,i),y=current.range(id,i);
    assert(prior.bytes.subarray(x.offset,x.offset+x.length).equals(current.bytes.subarray(y.offset,y.offset+y.length)),'exact current roof22/all-roof accessor preservation');
  }
}
export function triangles(g:GLB):Triangle[] {
  const out:Triangle[]=[];const d=g.document;const visited=new Set<number>();
  function visit(ni:number,parent:Matrix4) {
    assert(!visited.has(ni),'duplicate/cyclic scene node');visited.add(ni);const n=d.nodes[ni];
    const local=n.matrix?new Matrix4().fromArray(n.matrix):new Matrix4().compose(new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),new Vector3(...(n.scale??[1,1,1])));
    const world=parent.clone().multiply(local);
    if(n.mesh!==undefined)for(const p of d.meshes[n.mesh].primitives) {
      assert.equal(p.mode??4,4);const len=d.accessors[p.indices].count;assert.equal(len%3,0);
      const points=Array.from({length:d.accessors[p.attributes.POSITION].count},(_,i):P3=>{
        const v=new Vector3(...g.vec3(p.attributes.POSITION,i)).applyMatrix4(world);assert(v.toArray().every(Number.isFinite));return [v.x,-v.z,v.y];
      });
      for(let i=0;i<len;i+=3) {
        const q=g.triangle(p.indices,i/3).map(k=>points[k]) as [P3,P3,P3];assert(q.every(Boolean));
        const e1=q[1].map((v,k)=>v-q[0][k]) as P3,e2=q[2].map((v,k)=>v-q[0][k]) as P3;
        const cross=[e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0]];
        if(Math.hypot(...cross)/2<=1e-9)continue;
        out.push({owner:n.name,slot:i/3,points:q,e1,e2});
      }
    }
    for(const child of n.children??[])visit(child,world);
  }
  for(const ni of d.scenes[d.scene??0].nodes)visit(ni,new Matrix4());assert.equal(visited.size,d.nodes.length);return out;
}
// Double-sided geometry raycast: material color/opacity cannot make a missing
// opening, floor, soffit or return pass. Moller-Trumbore on live GLB triangles.
export function raycast(tris:Triangle[],origin:P3,direction:P3,maxDistance=100) {
  let distance=maxDistance,hit:Triangle|undefined;
  for(const t of tris) {
    const [ex,ey,ez]=t.e1,[fx,fy,fz]=t.e2,[dx,dy,dz]=direction;
    const px=dy*fz-dz*fy,py=dz*fx-dx*fz,pz=dx*fy-dy*fx,det=ex*px+ey*py+ez*pz;
    if(Math.abs(det)<1e-10)continue;
    const ix=origin[0]-t.points[0][0],iy=origin[1]-t.points[0][1],iz=origin[2]-t.points[0][2];
    const u=(ix*px+iy*py+iz*pz)/det;if(u< -1e-8||u>1+1e-8)continue;
    const qx=iy*ez-iz*ey,qy=iz*ex-ix*ez,qz=ix*ey-iy*ex;
    const v=(dx*qx+dy*qy+dz*qz)/det;if(v< -1e-8||u+v>1+1e-8)continue;
    const r=(fx*qx+fy*qy+fz*qz)/det;if(r>1e-7&&r<distance){distance=r;hit=t;}
  }
  return hit?{distance,owner:hit.owner,slot:hit.slot}:undefined;
}
export function basis(zone:typeof ZONES[number]) {
  const dx=zone.b[0]-zone.a[0],dy=zone.b[1]-zone.a[1],length=Math.hypot(dx,dy);
  const t:[number,number]=[dx/length,dy/length],n:[number,number]=[-t[1],t[0]];return {t,n,length};
}
export function assertApertures(tris:Triangle[]) {
  let count=0,min=Infinity,max=-Infinity;
  for(const z of ZONES) {
    const {t,n}=basis(z);
    for(const [lo,hi,bot,top] of z.rects)for(let i=1;i<=40;i++)for(let j=1;j<=20;j++) {
      const u=lo+(hi-lo)*i/41,h=bot+(top-bot)*j/21;
      const hit=raycast(tris,[z.a[0]+t[0]*u-n[0]*.5,z.a[1]+t[1]*u-n[1]*.5,h],[n[0],n[1],0]);
      assert(hit,`missing aperture back/return ${z.face}/${u}/${h}`);
      const depth=hit.distance-.5;assert(hit.owner.startsWith('prototype_terrace_'),`old front shell obstructs aperture ${z.face}: ${hit.owner}`);
      assert(!(depth>-.1&&depth<.1),'painted or shallow cover plane');assert(depth<25,'far-shell hollow terrace');
      min=Math.min(min,depth);max=Math.max(max,depth);count++;
    }
  }
  assert.equal(count,3200);return {count,min,max};
}
export function inside(p:P2,poly:P2[]) {
  let hit=false;for(let i=0;i<poly.length;i++) {
    const a=poly[i],b=poly[(i+1)%poly.length];
    if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])hit=!hit;
  }return hit;
}
export function assertFloorsAndCeilings(tris:Triangle[]) {
  let count=0;
  for(const key of ['east','corner','north']) {
    const poly=POLYGONS[key],floor=key==='north'?30.178:25.378,top=key==='east'?34.7:39.3;
    // Intersect the nominal slab planes, not the nearest stair/frame above them.
    const floorPlane=tris.filter(t=>t.owner==='prototype_terrace_floor'&&t.points.every(p=>Math.abs(p[2]-floor)<.00003));
    const soffitPlane=tris.filter(t=>t.owner==='prototype_terrace_structure'&&t.points.every(p=>Math.abs(p[2]-top)<.00003));
    for(let x=Math.floor(Math.min(...poly.map(p=>p[0])));x<Math.ceil(Math.max(...poly.map(p=>p[0])));x++)for(let y=Math.floor(Math.min(...poly.map(p=>p[1])));y<Math.ceil(Math.max(...poly.map(p=>p[1])));y++) {
      const p:P2=[x+.37,y+.41];if(!inside(p,poly)||inside(p,POLYGONS.core))continue;
      const down=raycast(floorPlane,[...p,floor+.1],[0,0,-1],1),up=raycast(soffitPlane,[...p,top-.1],[0,0,1],1);
      assert(down,`missing ${key} floor ${p}`);assert(up,`missing ${key} ceiling ${p}`);
      assert(Math.abs(down.distance-.1)<.00003,`wrong ${key} floor level`);assert(Math.abs(up.distance-.1)<.00003,`wrong ${key} soffit level`);count++;
    }
  }
  assert.equal(count,475);return count;
}
export function assertReturnsAndObliques(tris:Triangle[]) {
  let returns=0,obliques=0,maxDistance=0;
  for(const [a,b] of RETURNS) {
    const dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy),n=[-dy/len,dx/len];
    for(const u of [.05,.25,.5,.75,.95])for(const h of [30.3,32.5,36,39.1])for(const sign of [-1,1]) {
      assert(raycast(tris,[a[0]+dx*u+n[0]*sign*.5,a[1]+dy*u+n[1]*sign*.5,h],[-n[0]*sign,-n[1]*sign,0],1),'missing north termination return');returns++;
    }
  }
  const z=ZONES[2],{t,n,length}=basis(z);
  for(let i=1;i<75;i++) {
    const u=length*i/75;
    for(const h of u<11?[27,28.5,29.8,31,35,38.8]:[30.5,31,35,38.8])for(const deg of [15,30,45,60,75]) {
      const r=deg*Math.PI/180,hit=raycast(tris,[z.a[0]+t[0]*u-n[0]*.25,z.a[1]+t[1]*u-n[1]*.25,h],[n[0]*Math.cos(r)+n[1]*Math.sin(r),-n[0]*Math.sin(r)+n[1]*Math.cos(r),0]);
      assert(hit&&hit.distance<25,'open north oblique sightline into far shell');maxDistance=Math.max(maxDistance,hit.distance);obliques++;
    }
  }
  assert.equal(returns,80);assert.equal(obliques,1920);return {returns,obliques,maxDistance};
}
export const signedArea=(poly:P2[])=>poly.reduce((sum,a,i)=>{const b=poly[(i+1)%poly.length];return sum+a[0]*b[1]-b[0]*a[1];},0)/2;
const area=(poly:P2[])=>Math.abs(signedArea(poly));
const cross2=(a:P2,b:P2,p:P2)=>(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]);
export function clip(subject:P2[],raw:P2[]) {
  let out=[...subject];const boundary=signedArea(raw)<0?[...raw].reverse():raw;
  for(let i=0;i<boundary.length;i++) {
    const a=boundary[i],b=boundary[(i+1)%boundary.length],input=out;out=[];if(!input.length)break;
    let start=input[input.length-1],cs=cross2(a,b,start);
    for(const end of input) {
      const ce=cross2(a,b,end),inside=ce>=-1e-10,wasInside=cs>=-1e-10;
      if(inside!==wasInside){const t=cs/(cs-ce);out.push([start[0]+t*(end[0]-start[0]),start[1]+t*(end[1]-start[1])]);}
      if(inside)out.push(end);start=end;cs=ce;
    }
  }return out;
}
export function assertRetainedFragments(before:Triangle[],after:Triangle[]) {
  // Independent area-intersection proof from the original and current exported
  // triangles. It does not read the builder's cut audit or retained-fragment JSON.
  const entries=[
    {original:'parco_wall',retained:'prototype_terrace_retained',slots:{171:[195,451],108:[52,273],152:[128,372,373]}},
    {original:'parco_spandrel',retained:'prototype_terrace_retained_spandrel',slots:{171:[108,109,225,226],108:[],152:[84,85,201,202]}},
  ];
  const reports=[];
  for(const entry of entries) {
    const fragments=after.filter(t=>t.owner===entry.retained),claimed=new Set<Triangle>();
    for(const zone of ZONES) {
      const slots=entry.slots[zone.face as 171|108|152];if(!slots.length)continue;
      const old=before.filter(t=>t.owner===entry.original&&slots.includes(t.slot));assert.equal(old.length,slots.length);
      const {t}=basis(zone),project=(p:P3):P2=>[(p[0]-zone.a[0])*t[0]+(p[1]-zone.a[1])*t[1],p[2]];
      const rects=zone.rects.map(([lo,hi,bot,top]):P2[]=>[[lo,bot],[hi,bot],[hi,top],[lo,top]]);
      const removed=(poly:P2[])=>rects.reduce((sum,r)=>sum+area(clip(poly,r)),0);
      // Source spandrel ribbons have multiple parallel faces. Compare coverage
      // within their actual source plane, not just their 2D projection.
      const groups:{normal:Vector3;offset:number;old:Triangle[]}[]=[];
      for(const tri of old) {
        const normal=new Vector3(...tri.e1).cross(new Vector3(...tri.e2)).normalize(),offset=normal.dot(new Vector3(...tri.points[0]));
        let g=groups.find(g=>tri.points.every(p=>Math.abs(g.normal.dot(new Vector3(...p))-g.offset)<.00003));
        if(!g){g={normal,offset,old:[]};groups.push(g);}g.old.push(tri);
      }
      for(const group of groups) {
        const old2=group.old.map(v=>v.points.map(project));
        const actual=fragments.filter(v=>!claimed.has(v)&&v.points.every(p=>Math.abs(group.normal.dot(new Vector3(...p))-group.offset)<.00003));
        const expectedArea=old2.reduce((sum,p)=>sum+area(p)-removed(p),0);
        let actualArea=0;
        for(const tri of actual) {
          claimed.add(tri);const p=tri.points.map(project),size=area(p);actualArea+=size;
          const within=old2.reduce((sum,o)=>{const intersection=clip(p,o);return sum+area(intersection)-removed(intersection);},0);
          assert(Math.abs(size-within)<.002,`retained ${entry.original}/${zone.face} outside original or inside aperture`);
          assert(signedArea(p)*signedArea(old2[0])>0,'retained fragment winding');
        }
        for(let i=0;i<actual.length;i++)for(let j=i+1;j<actual.length;j++)assert(area(clip(actual[i].points.map(project),actual[j].points.map(project)))<.002,'retained fragment overlap');
        assert(Math.abs(actualArea-expectedArea)<.002,`retained ${entry.original}/${zone.face} missing outside-aperture area: ${actualArea}/${expectedArea}`);
        reports.push({owner:entry.original,face:zone.face,expectedArea,actualArea});
      }
    }
    assert.equal(claimed.size,fragments.length,'unattributed retained fragment');
  }
  return reports;
}
function subtractConvex(subject:P2[],raw:P2[]) {
  const boundary=signedArea(raw)<0?[...raw].reverse():raw,parts:P2[][]=[];let remaining=subject;
  for(let i=0;i<boundary.length;i++) {
    if(remaining.length<3)break;
    const a=boundary[i],b=boundary[(i+1)%boundary.length],inside:P2[]=[],outside:P2[]=[];
    let start=remaining[remaining.length-1],cs=cross2(a,b,start);
    for(const end of remaining) {
      const ce=cross2(a,b,end),yes=ce>=0,was=cs>=0;
      if(yes!==was){const t=cs/(cs-ce),p:P2=[start[0]+t*(end[0]-start[0]),start[1]+t*(end[1]-start[1])];inside.push(p);outside.push(p);}
      (yes?inside:outside).push(end);start=end;cs=ce;
    }
    if(area(outside)>1e-10)parts.push(outside);remaining=inside;
  }
  return parts;
}
export function assertCoreFloorCoverage(tris:Triangle[]) {
  const core=POLYGONS.core;
  const source=ShapeUtils.triangulateShape(core.map(p=>new Vector2(...p)),[]).map(t=>t.map(i=>core[i]));
  assert.equal(source.length,core.length-2);assert(Math.abs(source.reduce((s,p)=>s+area(p),0)-area(core))<1e-7);
  const covers=tris.filter(t=>t.owner==='prototype_terrace_floor'&&t.points.every(p=>Math.abs(p[2]-25.378)<.00003)).map(t=>t.points.map(p=>[p[0],p[1]] as P2));
  assert(covers.length>0,'missing current core floor');
  // Subtract the UNION of actual top triangles, rather than summing their areas:
  // an overlapping duplicate cannot compensate for a hole after core_base removal.
  let uncovered=source;
  for(const cover of covers)uncovered=uncovered.flatMap(p=>subtractConvex(p,cover));
  const uncoveredArea=uncovered.reduce((sum,p)=>sum+area(p),0);
  // At most 0.001 m² from decimal contract boundaries versus float32 GLB export,
  // not a modelling allowance. Exact serialized floor coverage is also verified
  // by the independent portable rational verifier in the production source.
  assert(uncoveredArea<.001,`missing core floor coverage ${uncoveredArea} m²`);
  assert(area(core)>170&&area(core)<173,'registered core plan bounds');return {coreArea:area(core),uncoveredArea};
}
