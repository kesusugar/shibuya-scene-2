import { Vector3 } from 'three';
// Independently bounded source91 plane in source XYZ (runtime is X,Z,-Y).
// These constants authorize only the accepted upper-overlay removal, never shell.
const origin = [277.214, -24.125, 0];
const tangent = [0.9463932686922139, 0.32301668838322745, 0];
const normal = [-0.32301668838322745, 0.9463932686922139, 0];
export function source91Coordinates(points: Vector3[]) {
  return points.map(p => {
    const r = [p.x-origin[0], -p.z-origin[1], p.y];
    return {u:r[0]*tangent[0]+r[1]*tangent[1],d:r[0]*normal[0]+r[1]*normal[1],z:r[2]};
  });
}
export function isSource91Overlay(points: Vector3[]) {
  const q=source91Coordinates(points);
  return q.every(p=>p.u>=-.0001&&p.u<=19.067126317303313+.0001&&p.d>=-.0001&&p.d<=.1201&&p.z>=101.0999&&p.z<=187.0001)
    && Math.max(...q.map(p=>p.d))-Math.min(...q.map(p=>p.d))<.0001;
}
export function isSource91Removal(points: Vector3[]) {
  const q=source91Coordinates(points),u=q.reduce((s,p)=>s+p.u,0)/3;
  return isSource91Overlay(points)&&q.every(p=>p.z>=112)&&!(u>=3&&u<=4.6);
}

