# QFRONT -> WebGL (glTF 2.0 / GLB) exporter.
#
#   blender -b assets/buildings/qfront/source/blend/qfront_v5_night.blend -P assets/buildings/qfront/source/blender/export_web.py -- <out.glb> [table.json]
#   blender -b assets/buildings/qfront/source/blend/qfront_v5_day.blend   -P assets/buildings/qfront/source/blender/export_web.py -- --table-only <table.json>
#
# The Cycles materials of build_qfront.py use node set-ups glTF cannot carry (light-path tricks, fresnel mixes,
# procedural bricks). Each material is rebuilt here as a plain Principled BSDF from its own parameters, so the GLB
# stays honest about what WebGL can show; the viewer adds the environment, sun and night lighting itself.
# Only the building is exported: the street context (09_CONTEXT) and people/vehicles (10_LIFE) stay in Blender.
import bpy, sys, json, os

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TABLE_ONLY = '--table-only' in argv
argv = [a for a in argv if a != '--table-only']

def principled_of(m):
    return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.use_nodes else None

def first_image(m):
    return next((n.image for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None) if m.use_nodes else None

def socket_value(sock):
    """Default value of a socket, or of input A of a Mix node feeding it (the streak/dirt mixes)."""
    if not sock.is_linked: return sock.default_value
    src = sock.links[0].from_node
    if src.type == 'MIX' and 'A' in src.inputs: return src.inputs['A'].default_value
    if src.type == 'MAP_RANGE': return src.inputs['To Min'].default_value
    if src.type == 'TEX_BRICK': return src.inputs['Color1'].default_value
    return sock.default_value

def describe(m):
    """Plain parameters for every material, from its Cycles node tree."""
    p = principled_of(m); nodes = {n.type for n in m.node_tree.nodes} if m.use_nodes else set()
    d = {'kind': 'opaque', 'base': [.5, .5, .5], 'metal': 0., 'rough': .5, 'emit': [0, 0, 0], 'estr': 0., 'alpha': 1., 'image': None, 'emit_image': None}
    if p:
        d['base'] = list(socket_value(p.inputs['Base Color']))[:3]; d['metal'] = float(socket_value(p.inputs['Metallic']))
        d['rough'] = float(socket_value(p.inputs['Roughness'])); d['emit'] = list(p.inputs['Emission Color'].default_value)[:3]
        d['estr'] = float(p.inputs['Emission Strength'].default_value)
        img = first_image(m)
        if img: d['image'] = img
        if p.inputs['Emission Color'].is_linked and img: d['emit_image'] = img; d['emit'] = [1, 1, 1]
    elif 'EMISSION' in nodes:          # LED screens: image x pixel mask -> emission
        em = next(n for n in m.node_tree.nodes if n.type == 'EMISSION')
        d.update(kind='led', base=[.02, .02, .025], rough=.25, emit=[1, 1, 1], estr=float(em.inputs['Strength'].default_value), image=None, emit_image=first_image(m))
    elif 'BSDF_TRANSPARENT' in nodes:  # glazing: tint x transmit + fresnel glossy
        # skip the shadow-ray pass-through (a Transparent BSDF mixed in by a Light Path node): it is not what the eye sees
        def is_shadow_pass(n):
            return any(l.to_node.type == 'MIX_SHADER' and l.to_node.inputs['Fac'].is_linked and l.to_node.inputs['Fac'].links[0].from_node.type == 'LIGHT_PATH'
                       and l.to_socket == l.to_node.inputs[2] for l in n.outputs['BSDF'].links)
        tr = next(n for n in m.node_tree.nodes if n.type == 'BSDF_TRANSPARENT' and not is_shadow_pass(n))
        if tr.inputs['Color'].is_linked:     # panel glass: tint x transmit lives in input A of a multiply mix
            c = list(tr.inputs['Color'].links[0].from_node.inputs['A'].default_value)[:3]
        else:
            c = list(tr.inputs['Color'].default_value)[:3]
        t = max(c)
        d.update(kind='glass', base=[min(1, v/max(t, 1e-3))*.08 for v in c], rough=.04, metal=.0, alpha=max(.15, min(.94, 1-t)))
    return d

table = {}
for m in bpy.data.materials:
    if m.users == 0: continue
    d = describe(m); table[m.name] = {'kind': d['kind'], 'emit': d['emit'], 'estr': d['estr']}

if TABLE_ONLY:
    json.dump(table, open(argv[0], 'w'), indent=1); print('TABLE', len(table)); sys.exit(0)

# ---- building only
for cname in ('09_CONTEXT', '10_LIFE'):
    c = bpy.data.collections.get(cname)
    if c:
        for o in list(c.all_objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'): bpy.data.objects.remove(o, do_unlink=True)

# ---- text -> mesh
bpy.ops.object.select_all(action='DESELECT')
fonts = [o for o in bpy.context.scene.objects if o.type == 'FONT']
for o in fonts: o.select_set(True)
if fonts:
    bpy.context.view_layer.objects.active = fonts[0]; bpy.ops.object.convert(target='MESH')

# ---- rebuild every used material as a plain Principled BSDF
for m in [m for m in bpy.data.materials if m.users]:
    d = describe(m)
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*d['base'], 1); b.inputs['Metallic'].default_value = d['metal']; b.inputs['Roughness'].default_value = d['rough']
    b.inputs['Emission Color'].default_value = (*d['emit'], 1); b.inputs['Emission Strength'].default_value = d['estr']
    if d['image']:
        tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = d['image']; nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    if d['emit_image']:
        tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = d['emit_image']; nt.links.new(tx.outputs['Color'], b.inputs['Emission Color'])
    if d['kind'] == 'glass':
        b.inputs['Alpha'].default_value = d['alpha']; m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else m.blend_method
        m.surface_render_method = 'BLENDED' if hasattr(m, 'surface_render_method') else None
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    m['qfront_kind'] = d['kind']

out_glb = argv[0]
os.makedirs(os.path.dirname(os.path.abspath(out_glb)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB', export_apply=True, export_lights=False, export_cameras=False,
                          export_extras=True, export_yup=True, export_image_format='AUTO')
if len(argv) > 1: json.dump(table, open(argv[1], 'w'), indent=1)
tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.context.scene.objects if o.type == 'MESH')
print('EXPORTED', out_glb, 'objects', sum(1 for o in bpy.context.scene.objects if o.type == 'MESH'), 'tris', tris, 'materials', sum(1 for m in bpy.data.materials if m.users))
