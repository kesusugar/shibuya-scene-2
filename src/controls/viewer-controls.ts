import { Object3D, PerspectiveCamera, Raycaster, Vector3 } from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';
import { planToWorld } from '../world/coords';
import type { ViewerHints } from '../world/buildings';

export type ControlMode = 'orbit' | 'walk';
const EYE = 1.6;

/** 360-degree orbit around the building, or free walking at eye height with simple wall collision. */
export class ViewerControls {
  mode: ControlMode = 'orbit';
  readonly orbit: OrbitControls;
  readonly walk: PointerLockControls;
  private keys = new Set<string>();
  private ray = new Raycaster();
  private obstacles: Object3D[] = [];
  private projectionOverride = false;

  constructor(private camera: PerspectiveCamera, dom: HTMLElement) {
    this.orbit = new OrbitControls(camera, dom);
    this.orbit.enableDamping = true;
    this.orbit.maxPolarAngle = Math.PI * 0.495;
    this.orbit.minDistance = 8; this.orbit.maxDistance = 600;
    this.walk = new PointerLockControls(camera, dom);
    dom.addEventListener('click', () => { if (this.mode === 'walk' && !this.walk.isLocked) this.walk.lock(); });
    addEventListener('keydown', (e) => this.keys.add(e.code));
    addEventListener('keyup', (e) => this.keys.delete(e.code));
    addEventListener('blur', () => this.keys.clear());
  }

  setObstacles(objs: Object3D[]) { this.obstacles = objs; }

  frameBuilding(h: ViewerHints) {
    const mid = planToWorld(h.arcMid);
    const n = planToWorld(h.arcNormal).normalize();
    this.clearProjectionOverride();
    this.orbit.target.copy(mid).addScaledVector(n, -12).setY(24);
    this.camera.position.copy(mid).addScaledVector(n, 62).add(new Vector3(22, 12, 0));
    this.orbit.update();
  }

  setMode(mode: ControlMode, h: ViewerHints) {
    this.mode = mode;
    this.orbit.enabled = mode === 'orbit';
    if (mode === 'walk') {
      this.clearProjectionOverride();
      const mid = planToWorld(h.arcMid);
      const n = planToWorld(h.arcNormal).normalize();
      this.camera.position.copy(mid).addScaledVector(n, 18).setY(EYE);
      this.camera.lookAt(mid.clone().setY(12));
    } else {
      if (this.walk.isLocked) this.walk.unlock();
      this.frameBuilding(h);
    }
  }

  /**
   * The camera fitted to the Q032 photo (2018): level, off-centre principal point, same vertical field of view.
   * Uses a shifted projection so the view matches the Cycles render and the photo.
   */
  q032View(h: ViewerHints) {
    const c = h.cameraQ032;
    const mid = h.arcMid, n = h.arcNormal, t: [number, number] = [-n[1], n[0]];
    const pos: [number, number] = [mid[0] + n[0] * c.D + t[0] * c.lat, mid[1] + n[1] * c.D + t[1] * c.lat];
    const yw = (c.yaw * Math.PI) / 180;
    const look: [number, number] = [-(n[0] * Math.cos(yw) + t[0] * Math.sin(yw)), -(n[1] * Math.cos(yw) + t[1] * Math.sin(yw))];
    this.setMode('orbit', h);
    this.orbit.enabled = false;
    this.camera.position.copy(planToWorld(pos, c.height_m));
    this.camera.fov = (2 * Math.atan(c.H / 2 / c.fpx) * 180) / Math.PI;
    this.camera.lookAt(planToWorld([pos[0] + look[0] * 100, pos[1] + look[1] * 100], c.height_m));
    this.camera.updateProjectionMatrix();
    const e = this.camera.projectionMatrix.elements;
    // three.js: ndc = (P * v).xy / -z, so the shift terms enter with a minus sign
    e[8] = -(e[0] * (c.cx - c.W / 2)) / c.fpx;
    e[9] = -(e[5] * (c.H / 2 - c.cy)) / c.fpx;
    this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert();
    this.projectionOverride = true;
  }

  clearProjectionOverride() {
    if (!this.projectionOverride) return;
    this.projectionOverride = false;
    this.camera.fov = 55;
    this.camera.updateProjectionMatrix();
  }

  hasProjectionOverride() { return this.projectionOverride; }

  update(dt: number) {
    if (this.mode === 'orbit') { if (this.orbit.enabled) this.orbit.update(); return; }
    const speed = (this.keys.has('ShiftLeft') || this.keys.has('ShiftRight') ? 9 : 2.2) * dt;
    const fwd = new Vector3(); this.camera.getWorldDirection(fwd); fwd.y = 0; fwd.normalize();
    const right = new Vector3().crossVectors(fwd, new Vector3(0, 1, 0)).normalize();
    const move = new Vector3();
    if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) move.add(fwd);
    if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) move.sub(fwd);
    if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) move.add(right);
    if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) move.sub(right);
    if (move.lengthSq() === 0) return;
    move.normalize();
    // stop 0.4 m short of any wall, glass or column at knee and chest height
    for (const y of [0.5, 1.3]) {
      this.ray.set(this.camera.position.clone().setY(y), move);
      this.ray.far = speed + 0.4;
      if (this.ray.intersectObjects(this.obstacles, true).length) return;
    }
    this.camera.position.addScaledVector(move, speed).setY(EYE);
  }
}
