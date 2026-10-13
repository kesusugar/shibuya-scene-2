// Use the existing M027 camera fit, with the same axes/datum offset as ViewerControls.fitView.
import {NodeIO} from '@gltf-transform/core';
import {readFileSync,writeFileSync} from 'node:fs';
import {BufferAttribute,BufferGeometry,DoubleSide,Matrix4,Mesh,MeshBasicMaterial,PerspectiveCamera,Raycaster,Vector2,Vector3} from 'three';
const hints=JSON.parse(readFileSync('assets/buildings/magnet/web/viewer.json')),c=hints.cameraFit;
const [yaw,pitch,roll]=[c.yaw,c.pitch,c.roll].map(v=>v*Math.PI/180),w=(x,y,z)=>new Vector3(x,z,-y);
const f=w(Math.sin(yaw)*Math.cos(pitch),Math.cos(yaw)*Math.cos(pitch),Math.sin(pitch)),right=w(Math.cos(yaw),-Math.sin(yaw),0),up=new Vector3().crossVectors(right,f);
const camera=new PerspectiveCamera(2*Math.atan(c.H/2/c.fpx)*180/Math.PI,c.W/c.H,.1,1000);
camera.position.copy(w(...c.pos)).add(new Vector3(0,hints.groundElevationTP-15,0));camera.up.copy(up.multiplyScalar(Math.cos(roll)).addScaledVector(right,Math.sin(roll)));camera.lookAt(camera.position.clone().add(f));camera.updateMatrixWorld();
const layout=JSON.parse(readFileSync('assets/street/drainage/source/data/layout.json'));
const root=(await new NodeIO().read('assets/street/drainage/web/drainage.glb')).getRoot(),pixels=[];
for(const n of root.listNodes())for(const p of n.getMesh()?.listPrimitives()??[]){if(p.getMaterial()?.getName().endsWith('repair'))continue;const pos=p.getAttribute('POSITION'),matrix=new Matrix4().fromArray(n.getWorldMatrix());for(let i=0;i<pos.getCount();i++){const q=new Vector3().fromArray(pos.getElement(i,[])).applyMatrix4(matrix).project(camera);pixels.push([(q.x+1)*c.W/2,(1-q.y)*c.H/2]);}}
const bounds=[Math.min(...pixels.map(p=>p[0])),Math.min(...pixels.map(p=>p[1])),Math.max(...pixels.map(p=>p[0])),Math.max(...pixels.map(p=>p[1]))];
const p=layout.cover.points[0],q=new Vector3(p.xy[0],p.ground_tp-15+layout.base_offset_m,-p.xy[1]).project(camera),centre=[(q.x+1)*c.W/2,(1-q.y)*c.H/2];
const report={reference:'M027 / original 1280x1707 pixels',input_centre:p.pixel,rendered_centre:centre,centre_delta_px:centre.map((v,i)=>v-p.pixel[i]),input_edge_horizontal_span_px:layout.cover.points[2].pixel[0]-layout.cover.points[1].pixel[0],rendered_metal_bounds_px:bounds,rendered_metal_horizontal_span_px:bounds[2]-bounds[0],caveat:'same input photo and existing building camera, not independent accuracy; frame included in model extent, partial occlusion and manually read edges; offset moves apparent centre'};
writeFileSync('evidence/c2-road-cover/projection-check.json',JSON.stringify(report,null,2)+'\n');console.log(report);
