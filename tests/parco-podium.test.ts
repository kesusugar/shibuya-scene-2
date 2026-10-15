import { describe, expect, it } from 'vitest';
import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';
import { NodeIO, type Primitive, type Node } from '@gltf-transform/core';
import { Matrix3, Matrix4, ShapeUtils, Vector2, Vector3 } from 'three';
import { LEVEL_BUDGET } from '../src/perf/budget';

// The complete shallow-podium contract is historical, not silently weakened for
// the later deep-terrace stage. All existing geometry, source108/152 repairs,
// roof22, budget, stats and manifest assertions below retain their exact values.
// The current live artifact has separate contracts in parco-terrace.test.ts;
// roof-repair-layers.test.ts still exercises its live roof22 geometry.
import { assertParcoHistoricalFixtures, historicalParcoPath } from './helpers/parco-stage-fixtures';
const base = 'assets/buildings/parco/';
const currentPath = historicalParcoPath('web/parco.glb');
const baselinePath = base + 'source/inputs/baseline.glb';
const priorPath = base + 'source/roof-repair-v1/prior.glb';
const PRIOR_SHA256 = 'f47ab16785534c40361c5f8e8014c0348919db8a5cb686ddafb6962ca0976c56';
const BASELINE_SHA256 = '9fa2046b02ac220b305c67241a19b607ea39d2e0a7beedd953cb0a761d3152e2';
const SOURCE_SHA256 = '031a66d351a04474ffef5346264e1871f50f6d292bdd898d20bce7ca6bb644a1';
const sha = (path: string) => createHash('sha256').update(readFileSync(path)).digest('hex');
const json = (path: string) => JSON.parse(readFileSync(path, 'utf8'));
const roofConfig = json(base + 'source/roof-repair-v1/repair-config.json');
const rawGLB = (path: string) => {
  const bytes = readFileSync(path);
  expect(bytes.toString('utf8', 0, 4)).toBe('glTF');
  expect(bytes.readUInt32LE(4)).toBe(2);
  expect(bytes.readUInt32LE(8)).toBe(bytes.length);
  expect(bytes.readUInt32LE(16)).toBe(0x4e4f534a);
  return JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString('utf8'));
};
const binaryGLB = (path: string) => {
  const bytes = readFileSync(path), offset = 20 + bytes.readUInt32LE(12);
  expect(bytes.readUInt32LE(offset + 4)).toBe(0x004e4942);
  return bytes.subarray(offset + 8, offset + 8 + bytes.readUInt32LE(offset));
};
const additions = ['parco_podium_cladding', 'parco_podium_joint', 'parco_podium_glass', 'parco_podium_rail_glass'];
const zones = [
  { face: 171, a: [-110.668, 276.864], b: [-119.881, 294.839], z0: 25.4, z1: 56.097 },
  { face: 108, a: [-118.839, 295.526], b: [-125.516, 307.472], z0: 26.2, z1: 56.097 },
  { face: 152, a: [-125.516, 307.472], b: [-144.222, 306.519], z0: 26.2, z1: 56.097 },
];
const inZone = (p: Vector3, zone: typeof zones[number]) => {
  // glTF (east, up, south) -> source (east, north, up).
  const dx = zone.b[0] - zone.a[0], dy = zone.b[1] - zone.a[1];
  const width = Math.hypot(dx, dy), ux = dx / width, uy = dy / width;
  const x = p.x - zone.a[0], y = -p.z - zone.a[1];
  const u = x * ux + y * uy, depth = x * uy - y * ux;
  return u >= -.04 && u <= width + .04 && p.y >= zone.z0 - .0001 && p.y <= zone.z1 + .0001
    && depth >= .03 - .0001 && depth <= .55 + .0001;
};
function worldPositions(node: Node, primitive: Primitive) {
  const a = primitive.getAttribute('POSITION')!;
  const matrix = new Matrix4().fromArray(node.getWorldMatrix());
  return Array.from({ length: a.getCount() }, (_, i) => new Vector3().fromArray(a.getElement(i, [])).applyMatrix4(matrix));
}
const repaired108: Record<number, number[]> = { 52: [291, 292, 295], 272: [291, 295, 298] };
const repaired152: Record<number, number[]> = { 367: [721, 723, 728], 368: [728, 732, 733], 370: [721, 728, 733], 372: [721, 733, 734], 373: [721, 734, 738] };
const repairedTriangles = { ...repaired108, ...repaired152 };
function triangleSignatures(node: Node, primitive: Primitive, omit: Set<number> = new Set()) {
  const semantics = primitive.listSemantics().sort();
  const matrix = new Matrix4().fromArray(node.getWorldMatrix());
  const normalMatrix = new Matrix3().getNormalMatrix(matrix);
  const positions = worldPositions(node, primitive);
  const quantize = (v: number) => Math.round(v * 100000); // 0.01 mm / 1e-5 normal units.
  const corners = positions.map((p, i) => semantics.map(semantic => {
    if (semantic === 'POSITION') return p.toArray().map(quantize).join(',');
    const values = primitive.getAttribute(semantic)!.getElement(i, []);
    if (semantic === 'NORMAL') return new Vector3().fromArray(values).applyMatrix3(normalMatrix).normalize().toArray().map(quantize).join(',');
    return values.map(quantize).join(',');
  }).join('|'));
  const indices = primitive.getIndices();
  const count = indices?.getCount() ?? corners.length;
  const output: string[] = [];
  expect(primitive.getMode()).toBe(4);
  expect(count % 3).toBe(0);
  for (let i = 0; i < count; i += 3) {
    if (omit.has(i / 3)) continue;
    const vertices = [0, 1, 2].map(k => corners[indices ? indices.getScalar(i + k) : i + k]);
    // Ignore index/triangle reordering, but preserve winding and corner attributes.
    output.push([0, 1, 2].map(k => [...vertices.slice(k), ...vertices.slice(0, k)].join(';')).sort()[0]);
  }
  return output.sort();
}
function compareMaterial(actual: unknown, expected: unknown, label: string): void {
  if (typeof expected === 'number') {
    expect(typeof actual, label).toBe('number');
    expect(Math.abs((actual as number) - expected), label).toBeLessThanOrEqual(.00001);
  } else if (Array.isArray(expected)) {
    expect(Array.isArray(actual), label).toBe(true);
    expect((actual as unknown[]).length, label).toBe(expected.length);
    expected.forEach((v, i) => compareMaterial((actual as unknown[])[i], v, `${label}[${i}]`));
  } else if (expected && typeof expected === 'object') {
    expect(actual, label).toBeTruthy();
    expect(Object.keys(actual as object).sort(), label).toEqual(Object.keys(expected).sort());
    for (const [key, value] of Object.entries(expected)) compareMaterial((actual as Record<string, unknown>)[key], value, `${label}.${key}`);
  } else expect(actual, label).toEqual(expected);
}

type P2 = [number, number];
const signedArea = (poly: P2[]) => poly.reduce((sum, a, i) => { const b = poly[(i + 1) % poly.length]; return sum + a[0] * b[1] - b[0] * a[1]; }, 0) / 2;
const cross2 = (a: P2, b: P2, p: P2) => (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]);
// Sutherland-Hodgman clipping, used only with convex rectangles/triangles.
function clipConvex(subject: P2[], rawClip: P2[]): P2[] {
  let out = [...subject];
  const clip = signedArea(rawClip) < 0 ? [...rawClip].reverse() : rawClip;
  for (let i = 0; i < clip.length; i++) {
    const a = clip[i], b = clip[(i + 1) % clip.length], input = out; out = [];
    if (!input.length) break;
    let start = input[input.length - 1], cs = cross2(a, b, start);
    for (const end of input) {
      const ce = cross2(a, b, end), inside = ce >= -1e-10, wasInside = cs >= -1e-10;
      if (inside !== wasInside) { const t = cs / (cs - ce); out.push([start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])]); }
      if (inside) out.push(end);
      start = end; cs = ce;
    }
  }
  return out;
}

// Load each artifact once in this test module; all assertions derive from these bytes.
const io = new NodeIO();
const baseline = (await io.read(baselinePath)).getRoot();
const current = (await io.read(currentPath)).getRoot();
const prior = (await io.read(priorPath)).getRoot();
const originalNodes = baseline.listNodes().filter(node => node.getMesh());
const currentNodes = current.listNodes().filter(node => node.getMesh());
const addedNodes = currentNodes.filter(node => !originalNodes.some(old => old.getName() === node.getName()));
const actualStats = currentNodes.reduce((total, node) => {
  for (const p of node.getMesh()!.listPrimitives()) {
    total.primitives++;
    total.triangles += (p.getIndices()?.getCount() ?? p.getAttribute('POSITION')!.getCount()) / 3;
  }
  return total;
}, { triangles: 0, primitives: 0, bytes: statSync(currentPath).size });

describe('PARCO bounded northeast podium: immutable shallow-stage preservation', () => {
  it('pins the original GLB and raw PLATEAU source and retains TP15 ground registration', () => {
    assertParcoHistoricalFixtures();
    expect(sha(baselinePath)).toBe(BASELINE_SHA256);
    expect(sha(priorPath)).toBe(PRIOR_SHA256);
    expect(sha(base + 'source/data/plateau.json')).toBe(SOURCE_SHA256);
    expect(sha(base + 'web/viewer.json')).toBe('8a727c450e07127326a23ecb45364f42787bb86c829bc89a215ed22336ec21be');
    const source = json(base + 'source/data/plateau.json');
    expect(source.ground_tp).toBe(23.4);
    expect(source.top_tp).toBe(124.8);
    expect(json(base + 'web/viewer.json').groundElevationTP).toBe(15);
    expect(originalNodes).toHaveLength(8);
  });

  it.each([
    { label: 'historical pinned prior: exactly the seven108/152 triangles and two152 normals', path: priorPath, roofLayer: false },
    { label: 'historical roof22 output: the same108/152 fixes plus the bounded RoofSurface22 layer', path: currentPath, roofLayer: true },
  ])('preserves every original byte and attribute outside $label', ({ path, roofLayer }) => {
    const testedNodes = (roofLayer ? current : prior).listNodes().filter(node => node.getMesh());
    const rawBefore = rawGLB(baselinePath), rawAfter = rawGLB(path);
    // Verify every original JSON entry and binary byte. Only audited uint16
    // indices and two152 normal x/z signs change in this expected copy.
    for (const key of ['nodes', 'meshes', 'materials', 'accessors', 'bufferViews']) {
      expect(rawAfter[key].slice(0, rawBefore[key].length), key).toEqual(rawBefore[key]);
    }
    const expectedBinary = Buffer.from(binaryGLB(baselinePath));
    const accessor = rawBefore.accessors[5], view = rawBefore.bufferViews[accessor.bufferView];
    expect(accessor.componentType).toBe(5123);
    const indexOffset = (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0);
    for (const [triangle, replacement] of Object.entries(repairedTriangles)) {
      replacement.forEach((value, corner) => expectedBinary.writeUInt16LE(value, indexOffset + (Number(triangle) * 3 + corner) * 2));
    }
    const oldWallIndices = originalNodes.find(n => n.getName() === 'parco_wall')!.getMesh()!.listPrimitives()[0].getIndices()!;
    for (const [vertex, expectedOwners] of Object.entries({ 733: [367], 734: [367, 368] })) {
      const owners: number[] = [];
      for (let i = 0; i < oldWallIndices.getCount(); i += 3) if ([0, 1, 2].some(k => oldWallIndices.getScalar(i + k) === Number(vertex))) owners.push(i / 3);
      expect(owners, `normal vertex${vertex} must belong only to invalid152 triangles`).toEqual(expectedOwners);
    }
    const normalAccessor = rawBefore.accessors[4], normalView = rawBefore.bufferViews[normalAccessor.bufferView];
    expect(normalAccessor.componentType).toBe(5126);
    const normalOffset = (normalView.byteOffset ?? 0) + (normalAccessor.byteOffset ?? 0);
    for (const vertex of [733, 734]) for (const axis of [0, 2]) {
      const offset = normalOffset + vertex * (normalView.byteStride ?? 12) + axis * 4;
      expectedBinary.writeFloatLE(-expectedBinary.readFloatLE(offset), offset);
    }
    if (roofLayer) {
      // Derive offsets from the original binary layout, not saved success flags.
      const roofIndex = rawBefore.accessors[roofConfig.index_accessor], roofIndexView = rawBefore.bufferViews[roofIndex.bufferView];
      expect(roofIndex.componentType).toBe(5123);
      const offset = (roofIndexView.byteOffset ?? 0) + (roofIndex.byteOffset ?? 0);
      for (const change of roofConfig.triangle_changes) change.new.forEach((value: number, corner: number) => {
        expectedBinary.writeUInt16LE(value, offset + (change.triangle * 3 + corner) * 2);
      });
      const normal = rawBefore.accessors[roofConfig.normal_accessor], normalView = rawBefore.bufferViews[normal.bufferView];
      expect(normal.componentType).toBe(5126);
      const normalOffset = (normalView.byteOffset ?? 0) + (normal.byteOffset ?? 0);
      for (const change of roofConfig.normal_changes) change.new.forEach((value: number, axis: number) => {
        expectedBinary.writeFloatLE(value, normalOffset + change.vertex * (normalView.byteStride ?? 12) + axis * 4);
      });
    }
    expect(binaryGLB(path).subarray(0, expectedBinary.length).equals(expectedBinary)).toBe(true);
    expect(rawAfter.scenes[rawAfter.scene ?? 0].nodes.slice(0, originalNodes.length)).toEqual(rawBefore.scenes[rawBefore.scene ?? 0].nodes);
    for (const old of originalNodes) {
      const matches = testedNodes.filter(node => node.getName() === old.getName());
      expect(matches, old.getName()).toHaveLength(1);
      const next = matches[0];
      const before = old.getMesh()!.listPrimitives(), after = next.getMesh()!.listPrimitives();
      expect(after, old.getName()).toHaveLength(before.length);
      before.forEach((p, i) => {
        expect(after[i].listSemantics().sort()).toEqual(p.listSemantics().sort());
        const omit = old.getName() === 'parco_wall' ? new Set(Object.keys(repairedTriangles).map(Number))
          : roofLayer && old.getName() === 'parco_roof' ? new Set<number>(roofConfig.triangle_changes.map((t: { triangle: number }) => t.triangle)) : new Set<number>();
        expect(triangleSignatures(next, after[i], omit), old.getName()).toEqual(triangleSignatures(old, p, omit));
        if (old.getName() === 'parco_wall') {
          for (const [triangle, replacement] of Object.entries(repairedTriangles)) {
            expect([0, 1, 2].map(k => after[i].getIndices()!.getScalar(Number(triangle) * 3 + k))).toEqual(replacement);
          }
        }
        expect(after[i].getMaterial()!.getName()).toBe(p.getMaterial()!.getName());
        const name = p.getMaterial()!.getName();
        const beforeMaterials = rawBefore.materials.filter((m: { name: string }) => m.name === name);
        const afterMaterials = rawAfter.materials.filter((m: { name: string }) => m.name === name);
        expect(beforeMaterials).toHaveLength(1); expect(afterMaterials).toHaveLength(1);
        compareMaterial(afterMaterials[0], beforeMaterials[0], name);
      });
    }
  });

  it('repairs source108 to its actual L polygon without outside fill, holes, overlap or invented vertices', () => {
    const source = json(base + 'source/data/plateau.json');
    const ring = (source.surfaces[108].ring as number[][]).slice(0, -1);
    const origin = ring[0], end = ring[5];
    const length = Math.hypot(end[0] - origin[0], end[1] - origin[1]);
    const ux = (end[0] - origin[0]) / length, uy = (end[1] - origin[1]) / length;
    const project = (p: number[]): P2 => [(p[0] - origin[0]) * ux + (p[1] - origin[1]) * uy, p[2] - origin[2]];
    const polygon = ring.map(project), width = polygon[5][0], elbow = polygon[2][0], step = polygon[3][1], top = polygon[1][1];
    // Independent exact decomposition of source108's six-corner L silhouette.
    const regions: P2[][] = [ [[0, 0], [width, 0], [width, step], [0, step]], [[0, step], [elbow, step], [elbow, top], [0, top]] ];
    const wall = currentNodes.find(n => n.getName() === 'parco_wall')!;
    const primitive = wall.getMesh()!.listPrimitives()[0], points = worldPositions(wall, primitive), indices = primitive.getIndices()!;
    const triangles = [52, 272, 273, 274].map(t => [0, 1, 2].map(k => {
      const v = points[indices.getScalar(t * 3 + k)], p = [v.x, -v.z, v.y];
      expect(ring.some(r => Math.hypot(...r.map((value, axis) => value - p[axis])) < .0001)).toBe(true);
      return project(p);
    }));
    for (const triangle of triangles) {
      expect(signedArea(triangle)).toBeLessThan(0); // Retain source-face winding.
      const area = Math.abs(signedArea(triangle));
      const inside = regions.reduce((sum, region) => sum + Math.abs(signedArea(clipConvex(triangle, region))), 0);
      // Decimal source vs float32 GLB is <.001m²; .002m² is not a modelling allowance.
      expect(Math.abs(area - inside)).toBeLessThan(.002);
    }
    for (let i = 0; i < triangles.length; i++) for (let j = i + 1; j < triangles.length; j++) {
      expect(Math.abs(signedArea(clipConvex(triangles[i], triangles[j])))).toBeLessThan(.002);
    }
    const area = triangles.reduce((sum, triangle) => sum + Math.abs(signedArea(triangle)), 0);
    expect(Math.abs(area - Math.abs(signedArea(polygon)))).toBeLessThan(.002);
    expect(Math.abs(signedArea(polygon))).toBeCloseTo(1040.3310091630028, 5);
  });

  it('repairs source152 without bridging its notch and preserves its three correct original triangles', () => {
    const source = json(base + 'source/data/plateau.json');
    const ring = (source.surfaces[152].ring as number[][]).slice(0, -1);
    const origin = ring[0], end = ring[1];
    const length = Math.hypot(end[0] - origin[0], end[1] - origin[1]);
    const ux = (end[0] - origin[0]) / length, uy = (end[1] - origin[1]) / length;
    const project = (p: number[]): P2 => [(p[0] - origin[0]) * ux + (p[1] - origin[1]) * uy, p[2] - origin[2]];
    const polygon = ring.map(project);
    // Independent earcut partition of the unchanged ten-corner source polygon,
    // not the builder's replacement triangles or a saved success flag.
    const partition = ShapeUtils.triangulateShape(polygon.map(p => new Vector2(...p)), []).map(t => t.map(i => polygon[i]));
    expect(partition).toHaveLength(8);
    const wall = currentNodes.find(n => n.getName() === 'parco_wall')!;
    const primitive = wall.getMesh()!.listPrimitives()[0], points = worldPositions(wall, primitive), indices = primitive.getIndices()!;
    for (const [id, original] of Object.entries({ 128: [721, 738, 739], 369: [727, 729, 732], 371: [723, 724, 728] })) {
      expect([0, 1, 2].map(k => indices.getScalar(Number(id) * 3 + k))).toEqual(original);
    }
    const triangles = [128, 367, 368, 369, 370, 371, 372, 373].map(t => [0, 1, 2].map(k => {
      const v = points[indices.getScalar(t * 3 + k)], p = [v.x, -v.z, v.y];
      expect(ring.some(r => Math.hypot(...r.map((value, axis) => value - p[axis])) < .0001)).toBe(true);
      return project(p);
    }));
    for (const triangle of triangles) {
      expect(signedArea(triangle)).toBeGreaterThan(0);
      const area = Math.abs(signedArea(triangle));
      const inside = partition.reduce((sum, region) => sum + Math.abs(signedArea(clipConvex(triangle, region))), 0);
      expect(Math.abs(area - inside)).toBeLessThan(.002);
    }
    for (let i = 0; i < triangles.length; i++) for (let j = i + 1; j < triangles.length; j++) {
      expect(Math.abs(signedArea(clipConvex(triangles[i], triangles[j])))).toBeLessThan(.002);
    }
    const area = triangles.reduce((sum, triangle) => sum + Math.abs(signedArea(triangle)), 0);
    expect(Math.abs(area - Math.abs(signedArea(polygon)))).toBeLessThan(.002);
    expect(Math.abs(signedArea(polygon))).toBeCloseTo(2782.81406131103, 5);
    const normals = primitive.getAttribute('NORMAL')!;
    for (const vertex of [733, 734]) {
      expect(normals.getElement(vertex, [])[0]).toBeLessThan(0);
      expect(normals.getElement(vertex, [])[2]).toBeLessThan(-.99);
    }
  });

  it('adds only four grouped podium meshes, wholly within the three bounded source-face strips', () => {
    expect(addedNodes.map(node => node.getName()).sort()).toEqual([...additions].sort());
    expect(currentNodes).toHaveLength(12);
    const seenFaces = new Set<number>();
    for (const node of addedNodes) {
      expect(node.getMesh()!.listPrimitives(), node.getName()).toHaveLength(1);
      for (const p of node.getMesh()!.listPrimitives()) {
        expect(p.getMaterial()!.getName()).toBe(node.getName());
        expect(p.getMode()).toBe(4);
        const points = worldPositions(node, p), indices = p.getIndices();
        const count = indices?.getCount() ?? points.length;
        expect(points.length).toBeGreaterThan(0);
        expect(points.every(v => v.toArray().every(Number.isFinite))).toBe(true);
        expect(points.every(v => zones.some(zone => inZone(v, zone))), node.getName()).toBe(true);
        for (let i = 0; i < count; i += 3) {
          const t = [0, 1, 2].map(k => points[indices ? indices.getScalar(i + k) : i + k]);
          expect(t.every(Boolean), node.getName()).toBe(true);
          const containing = zones.filter(zone => t.every(v => inZone(v, zone)));
          expect(containing.length, `${node.getName()} triangle ${i / 3} crosses zone/depth limits`).toBeGreaterThan(0);
          containing.forEach(zone => seenFaces.add(zone.face));
          const area2 = new Vector3().subVectors(t[1], t[0]).cross(new Vector3().subVectors(t[2], t[0])).length();
          expect(area2, `${node.getName()} degenerate triangle ${i / 3}`).toBeGreaterThan(1e-9);
        }
      }
    }
    expect([...seenFaces].sort()).toEqual([108, 152, 171]);
    expect(current.listTextures()).toHaveLength(0);
    expect(current.listMaterials().map(m => m.getName()).sort()).toEqual([...baseline.listMaterials().map(m => m.getName()), ...additions].sort());
  });

  it('retains the roof boundary and complete building height while adding no ground/upper-tower geometry', () => {
    const all = currentNodes.flatMap(node => node.getMesh()!.listPrimitives().flatMap(p => worldPositions(node, p)));
    const oldPoints = originalNodes.flatMap(node => node.getMesh()!.listPrimitives().flatMap(p => worldPositions(node, p)));
    // Preserve actual original bounds: its existing facade relief reaches ~1.98 mm
    // below the nominal source ground, so do not redefine source ground as GLB min.
    expect(Math.min(...all.map(p => p.y))).toBe(Math.min(...oldPoints.map(p => p.y)));
    expect(Math.max(...all.map(p => p.y))).toBe(Math.max(...oldPoints.map(p => p.y)));
    expect(Math.max(...all.map(p => p.y))).toBeCloseTo(109.8, 4);
    // Original roof identity outside the exact RoofSurface22 edits is checked above.
    // All positions/bounds and every off-target byte are preserved by the roof layer tests.
    expect(currentNodes.filter(node => node.getName() === 'parco_roof')).toHaveLength(1);
    const newPoints = addedNodes.flatMap(node => node.getMesh()!.listPrimitives().flatMap(p => worldPositions(node, p)));
    expect(newPoints.every(p => p.y >= 25.4 - .0001 && p.y <= 56.097 + .0001)).toBe(true);
  });

  it('measures actual shallow-stage triangles/draw primitives/bytes and matches its pinned stats and manifest', () => {
    expect(actualStats.triangles).toBeGreaterThan(5314);
    expect(actualStats.triangles - 5314).toBeLessThanOrEqual(10000);
    expect(actualStats.primitives).toBe(12);
    expect(actualStats.triangles).toBeLessThanOrEqual(LEVEL_BUDGET.B.triangles);
    expect(actualStats.primitives).toBeLessThanOrEqual(LEVEL_BUDGET.B.primitives);
    expect(actualStats.bytes).toBeLessThanOrEqual(LEVEL_BUDGET.B.bytes);
    const stats = json(historicalParcoPath('source/data/stats.json'));
    expect(stats.triangles).toBe(actualStats.triangles);
    expect(stats.primitives).toBe(actualStats.primitives);
    const manifest = json(historicalParcoPath('manifest.json'));
    expect(manifest.stats).toEqual(actualStats);
    expect(manifest.source_id).toBe('way/451564412');
    expect(manifest.plateau_id).toBe('bldg_e199100f-cb89-4a81-8e38-0abee12cb1d4');
    expect(manifest.level).toBe('B');
    for (const [path, value] of Object.entries(manifest.files) as [string, { bytes: number; sha256: string }][]) {
      expect(statSync(historicalParcoPath(path)).size, path).toBe(value.bytes);
      expect(sha(historicalParcoPath(path)), path).toBe(value.sha256);
    }
    expect(manifest.files['web/parco.glb'].sha256).toBe(sha(currentPath));
    expect(manifest.files['source/inputs/baseline.glb'].sha256).toBe(BASELINE_SHA256);
  });
});
