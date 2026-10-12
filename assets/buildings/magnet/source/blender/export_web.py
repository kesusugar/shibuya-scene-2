# MAGNET -> WebGL (glTF 2.0 / GLB) exporter, one GLB per group of collections.
#
#   blender -b <magnet_night.blend> -P export_web.py -- <out.glb> <collection-prefixes> [table.json]
#   blender -b <magnet_day.blend>   -P export_web.py -- --table-only <table.json>
#
# e.g. prefixes "01_,02_,03_,04_,05_,06_" -> magnet.glb, "08_SIGNS_2025" -> magnet_signs_2025.glb, "07_" -> eiraku.glb.
# As for QFRONT (assets/buildings/qfront/source/blender/export_web.py): every material is rebuilt as a plain Principled
# BSDF from its own Cycles parameters, glass becomes alpha-blended, LED/backlit faces keep their image as emission.
import bpy, sys, json, os

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TABLE_ONLY = '--table-only' in argv
argv = [a for a in argv if a != '--table-only']

def principled_of(m):
    return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.use_nodes else None

def first_image(m):
    return next((n.image for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None) if m.use_nodes else None

def socket_value(sock):
    """Plain value behind a socket: follows streak/dirt mixes to their base input and brick textures to their main colour."""
    if not sock.is_linked: return sock.default_value
    src = sock.links[0].from_node
    if src.type == 'MIX':
        a = next((i for i in src.inputs if i.name == 'A' and i.enabled), src.inputs['A'])
        return socket_value(a)
    if src.type == 'MAP_RANGE': return src.inputs['To Min'].default_value
    if src.type == 'TEX_BRICK': return src.inputs['Color1'].default_value
    return sock.default_value

def describe(m):
    p = principled_of(m); nodes = {n.type for n in m.node_tree.nodes} if m.use_nodes else set()
    d = {'kind': 'opaque', 'base': [.5, .5, .5], 'metal': 0., 'rough': .5, 'emit': [0, 0, 0], 'estr': 0., 'alpha': 1., 'image': None, 'emit_image': None}
    if p:
        bc = socket_value(p.inputs['Base Color'])
        d['base'] = list(bc)[:3] if hasattr(bc, '__len__') else [bc]*3
        d['metal'] = float(socket_value(p.inputs['Metallic'])); d['rough'] = float(socket_value(p.inputs['Roughness']))
        d['emit'] = list(p.inputs['Emission Color'].default_value)[:3]; d['estr'] = float(p.inputs['Emission Strength'].default_value)
        img = first_image(m)
        if img: d['image'] = img
        if p.inputs['Emission Color'].is_linked and img: d['emit_image'] = img; d['emit'] = [1, 1, 1]
        if p.inputs['Alpha'].is_linked: d['kind'] = 'cutout'
    elif 'EMISSION' in nodes:          # LED screens
        em = next(n for n in m.node_tree.nodes if n.type == 'EMISSION')
        d.update(kind='led', base=[.02, .02, .025], rough=.25, emit=[1, 1, 1], estr=float(em.inputs['Strength'].default_value), image=None, emit_image=first_image(m))
    elif 'BSDF_TRANSPARENT' in nodes:  # glazing (skip the shadow-ray pass-through Transparent BSDF)
        def is_shadow_pass(n):
            return any(l.to_node.type == 'MIX_SHADER' and l.to_node.inputs['Fac'].is_linked and l.to_node.inputs['Fac'].links[0].from_node.type == 'LIGHT_PATH'
                       and l.to_socket == l.to_node.inputs[2] for l in n.outputs['BSDF'].links)
        tr = next(n for n in m.node_tree.nodes if n.type == 'BSDF_TRANSPARENT' and not is_shadow_pass(n))
        c = list(tr.inputs['Color'].links[0].from_node.inputs['A'].default_value)[:3] if tr.inputs['Color'].is_linked else list(tr.inputs['Color'].default_value)[:3]
        t = max(c)
        d.update(kind='glass', base=[min(1, v/max(t, 1e-3))*.08 for v in c], rough=.04, metal=.0, alpha=max(.15, min(.94, 1-t)))
    return d

table = {}
for m in bpy.data.materials:
    if m.users == 0: continue
    d = describe(m); table[m.name] = {'kind': d['kind'], 'emit': d['emit'], 'estr': d['estr']}
if TABLE_ONLY:
    json.dump(table, open(argv[0], 'w'), indent=1); print('TABLE', len(table)); sys.exit(0)

out_glb, prefixes = argv[0], argv[1].split(',')
for c in list(bpy.data.collections):
    if not any(c.name.startswith(p) for p in prefixes):
        for o in list(c.all_objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA') or not o.users_collection or o.users_collection[0] == bpy.context.scene.collection: bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action='DESELECT')
fonts = [o for o in bpy.context.scene.objects if o.type == 'FONT']
for o in fonts: o.select_set(True)
if fonts: bpy.context.view_layer.objects.active = fonts[0]; bpy.ops.object.convert(target='MESH')

used = {m for o in bpy.context.scene.objects if o.type == 'MESH' for m in o.data.materials if m}
for m in used:
    d = describe(m); nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*d['base'], 1); b.inputs['Metallic'].default_value = d['metal']; b.inputs['Roughness'].default_value = d['rough']
    b.inputs['Emission Color'].default_value = (*d['emit'], 1); b.inputs['Emission Strength'].default_value = d['estr']
    if d['image']:
        tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = d['image']; nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
        if d['kind'] == 'cutout': nt.links.new(tx.outputs['Alpha'], b.inputs['Alpha'])
    if d['emit_image']:
        tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = d['emit_image']; nt.links.new(tx.outputs['Color'], b.inputs['Emission Color'])
    if d['kind'] == 'glass':
        b.inputs['Alpha'].default_value = d['alpha']
        if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface']); m['ss2_kind'] = d['kind']

os.makedirs(os.path.dirname(os.path.abspath(out_glb)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB', export_apply=True, export_lights=False, export_cameras=False,
                          export_extras=True, export_yup=True, export_image_format='AUTO')
if len(argv) > 2: json.dump({k: v for k, v in table.items() if k in {m.name for m in used}}, open(argv[2], 'w'), indent=1)
tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.context.scene.objects if o.type == 'MESH')
print('EXPORTED', out_glb, 'objects', sum(1 for o in bpy.context.scene.objects if o.type == 'MESH'), 'tris', tris, 'materials', len(used))
