import { Vector3 } from 'three';

/** Plan coordinates used by the Blender sources: x = east, y = north (metres). */
export type PlanXY = [number, number];

/** World convention of Shibuya Scene 2.0 (same as 1.0 and as glTF Y-up export): X = east, Y = up, Z = south. */
export function planToWorld([x, y]: PlanXY, height = 0): Vector3 {
  return new Vector3(x, height, -y);
}
