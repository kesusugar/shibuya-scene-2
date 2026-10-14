import {expect,it} from 'vitest';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Group,Mesh,PlaneGeometry,MeshStandardMaterial} from 'three';
import {loadExterior,replaceProvisionalFill} from '../src/world/exterior';
import {loadTactileSupplement} from '../src/world/tactileSupplement';
const fixture=()=>{const root=new Group();for(const name of ['ground_road','ground_sidewalk']){const m=new Mesh(new PlaneGeometry(),new MeshStandardMaterial());m.name=name;root.add(m);}return root;};
it('loads three independent street tiles and clears a partially missing set',async()=>{
 const good=await loadExterior(async()=>fixture());expect(good.ok).toBe(true);expect(good.stats.tiles).toBe(3);
 const failed=await loadExterior(async url=>{if(url.includes('middle'))throw Error('missing tile');return fixture();});expect(failed.ok).toBe(false);expect(failed.root.children).toHaveLength(0);
});
it('rejects a malformed tile and an unrelated tactile mesh',async()=>{
 expect((await loadExterior(async()=>new Group())).ok).toBe(false);
 expect((await loadTactileSupplement(async()=>fixture(),'outer')).ok).toBe(false);
});
it('preserves protected Core and original tactile byte for byte',()=>{
 const expected:Record<string,string>={'assets/ground/core/web/ground_core.glb':'37755dd24d3fe78418b3133210a6dc05ebe2c3c2f615b5a8bd22a4db6279dd32','assets/street/core/web/street_core.glb':'de970a9a1951dc7fb57213b5849c19de92000d9477a2a7948074c8ded08fcf9a','assets/street/tactile/web/tactile.glb':'1dc0e2774d8936e7c949286037e9e92de4f2a14ef8583147712dca3cbe1ad4d2'};
 for(const [path,hash] of Object.entries(expected))expect(createHash('sha256').update(readFileSync(path)).digest('hex')).toBe(hash);
});

it('keeps provisional Core fill on replacement failure and preserves measured streets on success',()=>{
 const root=fixture(),fill=new Group();fill.name='ground_fill';root.add(fill);
 expect(replaceProvisionalFill(root,false)).toBe(false);expect(fill.parent).toBe(root);
 const road=root.getObjectByName('ground_road'),sidewalk=root.getObjectByName('ground_sidewalk');
 expect(replaceProvisionalFill(root,true)).toBe(true);expect(fill.parent).toBeNull();
 expect(root.getObjectByName('ground_road')).toBe(road);expect(root.getObjectByName('ground_sidewalk')).toBe(sidewalk);
});
