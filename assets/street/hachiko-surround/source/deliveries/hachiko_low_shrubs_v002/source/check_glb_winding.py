#!/usr/bin/env python3
"""Read-only closed-component winding audit for uncompressed GLB triangle meshes.
Python 3.10+ standard library only. Does not repair, rewrite or execute model code.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import struct
import sys

class UnsupportedGLB(ValueError):
    """Malformed or unsupported input: the audit cannot certify it."""

_COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2),
               5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
_TYPES = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4,
          'MAT2': 4, 'MAT3': 9, 'MAT4': 16}


def parse_glb(blob: bytes):
    if len(blob) < 20:
        raise UnsupportedGLB('GLB is too short')
    magic, version, length = struct.unpack_from('<4sII', blob)
    if magic != b'glTF' or version != 2 or length != len(blob):
        raise UnsupportedGLB('Invalid GLB magic, version or declared byte length')
    chunks = []
    at = 12
    while at < length:
        if at + 8 > length:
            raise UnsupportedGLB('Truncated chunk header')
        size, kind = struct.unpack_from('<II', blob, at)
        at += 8
        if size % 4 or at + size > length:
            raise UnsupportedGLB('Invalid chunk size/alignment')
        chunks.append((kind, blob[at:at + size]))
        at += size
    if not chunks or chunks[0][0] != 0x4E4F534A:
        raise UnsupportedGLB('First chunk must be JSON')
    if sum(k == 0x4E4F534A for k, _ in chunks) != 1:
        raise UnsupportedGLB('Expected one JSON chunk')
    try:
        doc = json.loads(chunks[0][1].decode('utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise UnsupportedGLB('Invalid JSON chunk') from exc
    bins = [v for k, v in chunks if k == 0x004E4942]
    if len(bins) != 1:
        raise UnsupportedGLB('Expected one embedded BIN chunk')
    buffers = doc.get('buffers', [])
    if len(buffers) != 1 or 'uri' in buffers[0]:
        raise UnsupportedGLB('Only one embedded buffer is supported; no external fetches')
    declared = buffers[0].get('byteLength', -1)
    if not isinstance(declared, int) or declared < 0 or not declared <= len(bins[0]) <= declared + 3:
        raise UnsupportedGLB('Invalid embedded buffer byteLength')
    return doc, bins[0][:declared]


def accessor(doc, binary, index):
    try:
        if not isinstance(index, int) or index < 0:
            raise UnsupportedGLB('Accessor index must be nonnegative integer')
        acc = doc['accessors'][index]
        if 'sparse' in acc:
            raise UnsupportedGLB('Sparse accessors require materialization before this audit')
        view_index = acc['bufferView']
        if not isinstance(view_index, int) or view_index < 0:
            raise UnsupportedGLB('BufferView index must be nonnegative integer')
        view = doc['bufferViews'][view_index]
        if view.get('buffer', 0) != 0:
            raise UnsupportedGLB('Accessor references an external buffer')
        if 'EXT_meshopt_compression' in view.get('extensions', {}):
            raise UnsupportedGLB('Meshopt-compressed bufferView is unsupported')
        if acc.get('normalized', False):
            raise UnsupportedGLB('Normalized/quantized accessor is unsupported')
        fmt, width = _COMPONENTS[acc['componentType']]
        components = _TYPES[acc['type']]
        count = acc['count']
        offset = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
        stride = view.get('byteStride', width * components)
        view_start, view_length = view.get('byteOffset', 0), view['byteLength']
        if any(not isinstance(n, int) or n < 0 for n in [count, offset, stride, view_start, view_length]):
            raise UnsupportedGLB('Invalid accessor/view integer fields')
        required = width * components
        if stride < required or stride % width or offset % width:
            raise UnsupportedGLB('Invalid accessor stride/alignment')
        end = offset if count == 0 else offset + (count - 1) * stride + required
        if offset < view_start or end > view_start + view_length or view_start + view_length > len(binary):
            raise UnsupportedGLB('Accessor exceeds its bufferView')
        unpack = struct.Struct('<' + fmt * components).unpack_from
        return acc, [unpack(binary, offset + j * stride) for j in range(count)]
    except (KeyError, IndexError, TypeError, struct.error) as exc:
        raise UnsupportedGLB(f'Invalid accessor {index}') from exc


def component_audit(vertices, faces, *, abs_volume_epsilon=1e-12,
                    relative_volume_epsilon=1e-12):
    """Exact seam reconciliation, edge-connected triangles, centered Python float64.
    Inputs are read-only. Vertices are not approximately welded and no normals change.
    """
    if not all(math.isfinite(x) and x >= 0 for x in (abs_volume_epsilon, relative_volume_epsilon)):
        raise ValueError('Volume tolerances must be finite and nonnegative')
    if not all(len(v) == 3 and all(math.isfinite(float(x)) for x in v) for v in vertices):
        raise UnsupportedGLB('Nonfinite or non-VEC3 position')
    ids = {}
    unique = []
    remap = []
    for v in vertices:
        key = tuple(float(x) for x in v)
        if key not in ids:
            ids[key] = len(unique)
            unique.append(key)
        remap.append(ids[key])
    triangles = []
    for f in faces:
        if len(f) != 3 or any(not isinstance(i, int) or not 0 <= i < len(vertices) for i in f):
            raise UnsupportedGLB('Triangle index is invalid or out of bounds')
        triangles.append(tuple(remap[i] for i in f))
    parents = list(range(len(triangles)))
    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    edges = defaultdict(list)
    for fi, tri in enumerate(triangles):
        for j in range(3):
            a, b = tri[j], tri[(j + 1) % 3]
            edges[tuple(sorted((a, b)))].append((fi, a, b))
    for entries in edges.values():
        for fi, _, _ in entries[1:]:
            parents[root(fi)] = root(entries[0][0])
    groups = defaultdict(list)
    for fi in range(len(triangles)):
        groups[root(fi)].append(fi)
    results = []
    for component_id, face_ids in enumerate(groups.values()):
        local_edges = {}
        vertex_ids = set()
        degenerate = 0
        for fi in face_ids:
            tri = triangles[fi]
            vertex_ids.update(tri)
            a, b, c = [unique[i] for i in tri]
            ab = tuple(b[i] - a[i] for i in range(3))
            ac = tuple(c[i] - a[i] for i in range(3))
            cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
            if len(set(tri)) < 3 or all(x == 0 for x in cross):
                degenerate += 1
            for j in range(3):
                key = tuple(sorted((tri[j], tri[(j+1) % 3])))
                local_edges[key] = edges[key]
        boundary = sum(len(e) == 1 for e in local_edges.values())
        nonmanifold = sum(len(e) > 2 for e in local_edges.values())
        inconsistent = sum(len(e) == 2 and (e[0][1], e[0][2]) == (e[1][1], e[1][2]) for e in local_edges.values())
        closed = bool(local_edges) and boundary == 0 and nonmanifold == 0
        consistent = inconsistent == 0
        # Stable center and float64 scalar arithmetic, never float32 origin-based dot/cross.
        vv = [unique[i] for i in sorted(vertex_ids)]
        center = tuple(math.fsum(v[i] for v in vv) / len(vv) for i in range(3))
        extent = tuple(max(v[i] for v in vv) - min(v[i] for v in vv) for i in range(3))
        terms = []
        for fi in face_ids:
            a, b, c = [tuple(unique[k][i] - center[i] for i in range(3)) for k in triangles[fi]]
            terms.append(a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0]))
        volume = math.fsum(terms) / 6
        epsilon = max(abs_volume_epsilon, relative_volume_epsilon * max(extent, default=0)**3)
        if degenerate:
            state = 'degenerate'
        elif nonmanifold:
            state = 'nonmanifold'
        elif not consistent:
            state = 'inconsistent'
        elif not closed:
            state = 'open'
        elif volume < -epsilon:
            state = 'inward'
        elif volume > epsilon:
            state = 'outward'
        else:
            state = 'indeterminate_volume'
        results.append({'component': component_id, 'triangles': len(face_ids), 'vertices': len(vv),
                        'closed': closed, 'consistent': consistent, 'boundary_edges': boundary,
                        'nonmanifold_edges': nonmanifold, 'inconsistent_edges': inconsistent,
                        'degenerate_triangles': degenerate, 'state': state,
                        'signed_volume': volume, 'volume_epsilon': epsilon,
                        'extent': extent, 'center': center,
                        # Volume does not establish orientation for an open/inconsistent surface.
                        'volume_interpretable': closed and consistent and degenerate == 0})
    return results


def audit_glb(blob, *, abs_volume_epsilon=1e-12, relative_volume_epsilon=1e-12):
    doc, binary = parse_glb(blob)
    if doc.get('asset', {}).get('version') != '2.0':
        raise UnsupportedGLB('glTF asset.version must be 2.0')
    meshes = []
    for mi, mesh in enumerate(doc.get('meshes', [])):
        vertices, faces, materials = [], [], []
        for pi, primitive in enumerate(mesh.get('primitives', [])):
            if primitive.get('mode', 4) != 4:
                raise UnsupportedGLB(f'Mesh {mi}, primitive {pi}: only TRIANGLES mode is supported')
            if 'KHR_draco_mesh_compression' in primitive.get('extensions', {}):
                raise UnsupportedGLB('Draco-compressed geometry is unsupported')
            if primitive.get('targets'):
                raise UnsupportedGLB('Morph target geometry requires separate validation')
            try:
                acc, points = accessor(doc, binary, primitive['attributes']['POSITION'])
            except KeyError as exc:
                raise UnsupportedGLB('Primitive lacks POSITION') from exc
            if acc['type'] != 'VEC3' or acc['componentType'] != 5126:
                raise UnsupportedGLB('Only float32 VEC3 POSITION is supported')
            if 'indices' in primitive:
                ia, values = accessor(doc, binary, primitive['indices'])
                if ia['type'] != 'SCALAR' or ia['componentType'] not in (5121, 5123, 5125):
                    raise UnsupportedGLB('Indices must be unsigned scalar integers')
                indices = [v[0] for v in values]
            else:
                indices = list(range(len(points)))
            if len(indices) % 3:
                raise UnsupportedGLB('TRIANGLES index count is not a multiple of three')
            if any(i < 0 or i >= len(points) for i in indices):
                raise UnsupportedGLB('Primitive index exceeds POSITION count')
            base = len(vertices)
            vertices.extend(points)
            faces.extend(tuple(base + i for i in indices[j:j+3]) for j in range(0, len(indices), 3))
            material_id = primitive.get('material')
            if material_id is not None and (not isinstance(material_id, int) or not 0 <= material_id < len(doc.get('materials', []))):
                raise UnsupportedGLB('Invalid material index')
            material = doc.get('materials', [])[material_id] if material_id is not None else {}
            materials.append({'primitive': pi, 'material': material_id, 'name': material.get('name'),
                              'doubleSided': material.get('doubleSided', False),
                              'alphaMode': material.get('alphaMode', 'OPAQUE'),
                              'transmission': 'KHR_materials_transmission' in material.get('extensions', {})})
        if not faces:
            raise UnsupportedGLB(f'Mesh {mi} contains no triangles')
        components = component_audit(vertices, faces, abs_volume_epsilon=abs_volume_epsilon,
                                     relative_volume_epsilon=relative_volume_epsilon)
        meshes.append({'mesh': mi, 'name': mesh.get('name'), 'triangles': len(faces),
                       'materials': materials, 'components': components})
    if not meshes:
        raise UnsupportedGLB('No triangle meshes to validate')
    counts = Counter(c['state'] for mesh in meshes for c in mesh['components'])
    errors = sum(n for state, n in counts.items() if state not in ('outward', 'open'))
    return {'schema_version': 1, 'method': 'exact-position seam reconciliation; edge-connected components; centered float64 math.fsum',
            'scope': 'mesh-local bind geometry, across material primitives within each mesh; no node/skin/morph simulation',
            'abs_volume_epsilon': abs_volume_epsilon, 'relative_volume_epsilon': relative_volume_epsilon,
            'counts': dict(counts), 'error_components': errors,
            'negative_closed_components': counts['inward'],
            'topology_review_components': sum(c['state'] in ('nonmanifold', 'inconsistent', 'degenerate') for m in meshes for c in m['components']),
            'indeterminate_closed_components': counts['indeterminate_volume'],
            'status': 'fail' if errors else ('pass_with_open_surfaces' if counts['open'] else 'pass'),
            'meshes': meshes}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('glb', type=Path)
    parser.add_argument('--json', type=Path, help='Optional JSON report destination; input GLB is never changed')
    parser.add_argument('--require-closed', action='store_true', help='Treat open surfaces as failure (not appropriate for intentional sheets)')
    parser.add_argument('--abs-volume-epsilon', type=float, default=1e-12)
    parser.add_argument('--relative-volume-epsilon', type=float, default=1e-12)
    args = parser.parse_args(argv)
    try:
        if args.json and (args.json.resolve() == args.glb.resolve() or
                          (args.json.exists() and args.glb.exists() and args.json.samefile(args.glb))):
            raise UnsupportedGLB('JSON output cannot overwrite the input GLB')
        report = audit_glb(args.glb.read_bytes(), abs_volume_epsilon=args.abs_volume_epsilon,
                           relative_volume_epsilon=args.relative_volume_epsilon)
        report['file'] = str(args.glb)
        if args.require_closed and report['counts'].get('open', 0):
            report['status'] = 'fail_open_surfaces'
        if args.json:
            args.json.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        print(json.dumps({k: report[k] for k in ('file', 'status', 'counts', 'negative_closed_components', 'topology_review_components', 'error_components')}))
        return 0 if report['status'].startswith('pass') else 1
    except (UnsupportedGLB, OSError, ValueError, IndexError, TypeError, OverflowError) as exc:
        print(json.dumps({'status': 'unsupported_or_invalid', 'error': str(exc)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
