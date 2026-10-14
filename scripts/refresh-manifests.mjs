// Refresh selected asset manifests from exported GLBs; preserve existing provenance fields.
import {NodeIO} from '@gltf-transform/core';
import {readFileSync,writeFileSync,readdirSync,statSync,existsSync} from 'node:fs';
import {join,relative} from 'node:path';
import {createHash} from 'node:crypto';
for(const base of process.argv.slice(2)){
 const io=new NodeIO();let triangles=0,primitives=0,bytes=0;
 for(const name of readdirSync(join(base,'web')).filter(n=>n.endsWith('.glb'))){const p=join(base,'web',name),root=(await io.read(p)).getRoot();bytes+=statSync(p).size;for(const n of root.listNodes())for(const q of n.getMesh()?.listPrimitives()??[]){primitives++;triangles+=(q.getIndices()?.getCount()??q.getAttribute('POSITION').getCount())/3;}}
 const path=join(base,'manifest.json'),m=existsSync(path)?JSON.parse(readFileSync(path)): {id:base.replace('assets/','').replace('buildings/',''),level:base.includes('/ground/')?'ground':'B',status:'prototype; see README for evidence and estimates'};
 const files={};function walk(dir){for(const e of readdirSync(dir,{withFileTypes:true})){if(['manifest.json','__pycache__'].includes(e.name))continue;const p=join(dir,e.name);if(e.isDirectory())walk(p);else files[relative(base,p)]={bytes:statSync(p).size,sha256:createHash('sha256').update(readFileSync(p)).digest('hex')};}}walk(base);m.stats={triangles,primitives,bytes};m.files=files;writeFileSync(path,JSON.stringify(m,null,2)+'\n');console.log(m.id,m.stats);
}
