import { describe, expect, it } from 'vitest';
import { BoxGeometry, Group, Mesh, MeshBasicMaterial, PerspectiveCamera, PlaneGeometry, Vector3 } from 'three';
import { MAX_STEP, ViewerControls } from '../src/controls/viewer-controls';

(globalThis as unknown as Record<string, unknown>).addEventListener ??= () => {};
(globalThis as unknown as Record<string, unknown>).removeEventListener ??= () => {};
// Plan: flat ground y=0 for x<2, a kerb of `rise` for 2<=x<4, nothing beyond x=4; a post at x=-3.
function rig(rise: number) {
  const doc = { addEventListener() {}, removeEventListener() {}, pointerLockElement: null };
  const dom = { addEventListener() {}, removeEventListener() {}, getRootNode: () => doc, ownerDocument: doc, style: {}, setPointerCapture() {}, releasePointerCapture() {} } as unknown as HTMLElement;
  const camera = new PerspectiveCamera();
  const c = new ViewerControls(camera, dom);
  const g = new Group(); const m = new MeshBasicMaterial();
  const low = new Mesh(new PlaneGeometry(12, 10), m); low.rotation.x = -Math.PI / 2; low.position.set(-4, 0, 0);
  const high = new Mesh(new PlaneGeometry(2, 10), m); high.rotation.x = -Math.PI / 2; high.position.set(3, rise, 0);
  g.add(low, high); g.updateMatrixWorld(true);
  const post = new Mesh(new BoxGeometry(0.3, 2, 0.3), m); post.position.set(-3, 1, 0); post.updateMatrixWorld(true);
  c.setGround([g]); c.setObstacles([post]);
  return c;
}
const east = new Vector3(1, 0, 0), west = new Vector3(-1, 0, 0);

describe('walking', () => {
  it('climbs a kerb up to MAX_STEP and follows it', () => {
    const c = rig(0.15); const p = c.stepTo(new Vector3(1.8, 1.6, 0), east, 0.4)!;
    expect(p).not.toBeNull(); expect(p.y).toBeCloseTo(0.15 + 1.6, 5);
  });
  it('refuses a rise higher than MAX_STEP instead of teleporting onto it', () => {
    const c = rig(MAX_STEP + 0.3); expect(c.stepTo(new Vector3(1.8, 1.6, 0), east, 0.4)).toBeNull();
  });
  it('stops at the edge of the walking surface instead of dropping to y = 0', () => {
    const c = rig(0.15); expect(c.stepTo(new Vector3(3.8, 1.75, 0), east, 0.4)).toBeNull();
  });
  it('is blocked by registered furniture such as the statue or a kiosk', () => {
    const c = rig(0.15); expect(c.stepTo(new Vector3(-2.3, 1.6, 0), west, 0.3)).toBeNull();
    expect(c.stepTo(new Vector3(0, 1.6, 0), west, 0.3)).not.toBeNull();
  });
});
