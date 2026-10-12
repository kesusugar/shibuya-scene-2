// Refresh provenance hashes and geometry counts after regenerating C2b assets.
import { NodeIO } from '@gltf-transform/core';
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
const io = new NodeIO();
async function measure(dir) {
  const files = {}; let triangles = 0, primitives = 0, bytes = 0;
  for (const file of readdirSync(dir).filter((f) => f.endsWith('.glb')).sort()) {
    const root = (await io.read(join(dir, file))).getRoot(); let t = 0, p = 0;
    for (const mesh of root.listMeshes()) for (const prim of mesh.listPrimitives()) { p++; t += (prim.getIndices()?.getCount() ?? prim.getAttribute('POSITION').getCount()) / 3; }
    const b = statSync(join(dir, file)).size; files[file] = { triangles: t, primitives: p, bytes: b };
    triangles += t; primitives += p; bytes += b;
  }
  return { triangles, primitives, bytes, files };
}
const budget = {};
for (const [category, prefix] of [['buildings', ''], ['ground', 'ground/'], ['street', 'street/']]) {
  for (const id of readdirSync(`assets/${category}`)) if (existsSync(`assets/${category}/${id}/web`)) budget[prefix + id] = await measure(`assets/${category}/${id}/web`);
}
budget.total = Object.values(budget).reduce((s, v) => ({ triangles: s.triangles + v.triangles, primitives: s.primitives + v.primitives, bytes: s.bytes + v.bytes }), { triangles: 0, primitives: 0, bytes: 0 });
const base = 'assets/street/core', hashes = {};
function walk(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (e.name === '__pycache__' || e.name === 'manifest.json') continue;
    const path = join(dir, e.name);
    if (e.isDirectory()) walk(path);
    else hashes[relative(base, path)] = { bytes: statSync(path).size, sha256: createHash('sha256').update(readFileSync(path)).digest('hex') };
  }
}
walk(base);
const manifest = {
  id: 'street/core', status: 'C2b prototype; photo placements experimental only', fidelity: 'B', datum_tp_m: 15,
  tools: { Blender: '4.2.3 LTS', glTF: 'bundled exporter', addons: [] }, stats: budget['street/core'], files: hashes,
  sources: { osm: { query_date: '2025-10-31T23:59:59Z', license: 'ODbL-1.0', attribution: '© OpenStreetMap contributors', file: 'source/data/osm_2025.json' }, photos: 'source/refs/REFERENCE_REGISTER.csv' },
  limitations: ['Five named entrance POIs plus one unidentified candidate; shape and height remain provisional.', 'Mapped tree nodes are not a complete vegetation inventory.', 'Photo-projected equipment is opt-in amber: calibration variants differ by up to 2.861m.', 'No vehicle-signal support is inferred from a logical OSM road-signal node.', 'Light head type, height and 1800cd output remain unverified.'],
};
writeFileSync(`${base}/manifest.json`, JSON.stringify(manifest, null, 2) + '\n');
writeFileSync('evidence/c2b/budget.json', JSON.stringify(budget, null, 2) + '\n');
console.log('street', budget['street/core'], 'core total', budget.total);
