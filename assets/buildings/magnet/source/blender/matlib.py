# Shared material and mesh helpers, lifted unchanged from the QFRONT v5 generator
# (assets/buildings/qfront/source/blender/build_qfront.py, lines 71-169 and 271-327) so MAGNET renders with the
# same shading model. Set matlib.NIGHT before calling printed(); Builder.finish() needs matlib.MAT filled.
import bpy, bmesh, math
from mathutils import Vector, Matrix
NIGHT = False
MAT = {}; COL = {}

def node_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); return m, nt, out

def principled(name, col, metal=0., rough=.5, emit=None, estr=0., streaks=0.):
    m, nt, out = node_mat(name); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
    if streaks:
        # Rain streaks: noise stretched vertically in object space darkens and roughens the finish.
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (6, 6, .25)
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3; nz.inputs['Detail'].default_value = 6
        cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = .45; cr.color_ramp.elements[1].position = .75
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['A'].default_value = (*col, 1)
        mix.inputs['B'].default_value = (col[0]*(1-streaks), col[1]*(1-streaks), col[2]*(1-streaks*.9), 1)
        nt.links.new(cr.outputs['Color'], mix.inputs['Factor']); nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
        rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rough; rr.inputs['To Max'].default_value = rough+.25
        nt.links.new(cr.outputs['Color'], rr.inputs['Value']); nt.links.new(rr.outputs['Result'], b.inputs['Roughness'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface']); return m

def shadow_through(nt, shader, out, tint):
    """v5 fix (found while matching the podium): shadow rays see a plain, slightly tinted transparent pane, so sunlight
    reaches the rooms and the blinds behind glass. v4 let the fresnel/glossy mix block a large share of the sun."""
    lp = nt.nodes.new('ShaderNodeLightPath'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (.4 + .55*tint[0], .4 + .55*tint[1], .4 + .55*tint[2], 1)
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs['Fac']); nt.links.new(shader.outputs['Shader'], mx.inputs[1]); nt.links.new(tr.outputs['BSDF'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])

def glass(name, tint, transmit, rough=.02, ior=1.9):
    """Thin architectural glazing: fresnel mix of a sharp reflection and a tinted see-through."""
    m, nt, out = node_mat(name)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (tint[0]*transmit, tint[1]*transmit, tint[2]*transmit, 1)
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = rough; gl.inputs['Color'].default_value = (.9, .9, .9, 1)
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = ior    # coated panes reflect more than plain glass
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(fr.outputs['Fac'], mx.inputs['Fac']); nt.links.new(tr.outputs['BSDF'], mx.inputs[1]); nt.links.new(gl.outputs['BSDF'], mx.inputs[2])
    shadow_through(nt, mx, out, tint); return m

def panel_glass(name, tint, transmit, ior, pw, ph, rough=.012, wobble=.035, streak=.5, base=None):
    """Curtain-wall glazing that is not one perfect mirror: every pane (pw x ph m, from the ribbon UVs in metres) gets its
    own slight tilt, roughness, reflectance and see-through; faint vertical rain streaks roughen and dull it."""
    m, nt, out = node_mat(name); L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); geo = nt.nodes.new('ShaderNodeNewGeometry')
    dv = nt.nodes.new('ShaderNodeVectorMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = (pw, ph, 1)
    fl = nt.nodes.new('ShaderNodeVectorMath'); fl.operation = 'FLOOR'
    wn = nt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '3D'
    L(tc.outputs['UV'], dv.inputs[0]); L(dv.outputs['Vector'], fl.inputs[0]); L(fl.outputs['Vector'], wn.inputs['Vector'])
    sep = nt.nodes.new('ShaderNodeSeparateColor'); L(wn.outputs['Color'], sep.inputs['Color'])
    # per-pane normal wobble: N + (rand - .5) * wobble
    sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (.5, .5, .5)
    L(wn.outputs['Color'], sub.inputs[0])
    sc_ = nt.nodes.new('ShaderNodeVectorMath'); sc_.operation = 'SCALE'; sc_.inputs['Scale'].default_value = wobble; L(sub.outputs['Vector'], sc_.inputs[0])
    ad = nt.nodes.new('ShaderNodeVectorMath'); ad.operation = 'ADD'; L(geo.outputs['Normal'], ad.inputs[0]); L(sc_.outputs['Vector'], ad.inputs[1])
    nm = nt.nodes.new('ShaderNodeVectorMath'); nm.operation = 'NORMALIZE'; L(ad.outputs['Vector'], nm.inputs[0])
    # vertical streaks (UV stretched in v)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (7, .25, 1); L(tc.outputs['UV'], mp.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.5; nz.inputs['Detail'].default_value = 5; L(mp.outputs['Vector'], nz.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = .5; cr.inputs['From Max'].default_value = .75; L(nz.outputs['Fac'], cr.inputs['Value'])
    # roughness = rough + .03*r + .05*streak
    r1 = nt.nodes.new('ShaderNodeMath'); r1.operation = 'MULTIPLY_ADD'; r1.inputs[1].default_value = .03; r1.inputs[2].default_value = rough; L(sep.outputs['Red'], r1.inputs[0])
    r2 = nt.nodes.new('ShaderNodeMath'); r2.operation = 'MULTIPLY_ADD'; r2.inputs[1].default_value = .05*streak; L(cr.outputs['Result'], r2.inputs[0]); L(r1.outputs['Value'], r2.inputs[2])
    # reflectance tint = .72 + .25*g - .12*streak
    g1 = nt.nodes.new('ShaderNodeMath'); g1.operation = 'MULTIPLY_ADD'; g1.inputs[1].default_value = .25; g1.inputs[2].default_value = .72; L(sep.outputs['Green'], g1.inputs[0])
    g2 = nt.nodes.new('ShaderNodeMath'); g2.operation = 'MULTIPLY_ADD'; g2.inputs[1].default_value = -.12*streak; L(cr.outputs['Result'], g2.inputs[0]); L(g1.outputs['Value'], g2.inputs[2])
    gc = nt.nodes.new('ShaderNodeCombineColor'); [L(g2.outputs['Value'], gc.inputs[i]) for i in range(3)]
    # see-through = transmit * (.45 + 1.1*b)
    b1 = nt.nodes.new('ShaderNodeMath'); b1.operation = 'MULTIPLY_ADD'; b1.inputs[1].default_value = 1.1; b1.inputs[2].default_value = .45; L(sep.outputs['Blue'], b1.inputs[0])
    tcol = nt.nodes.new('ShaderNodeMix'); tcol.data_type = 'RGBA'; tcol.blend_type = 'MULTIPLY'; tcol.inputs['Factor'].default_value = 1
    tcol.inputs['A'].default_value = (tint[0]*transmit, tint[1]*transmit, tint[2]*transmit, 1); L(b1.outputs['Value'], tcol.inputs['B'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); L(tcol.outputs['Result'], tr.inputs['Color'])
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); L(r2.outputs['Value'], gl.inputs['Roughness']); L(gc.outputs['Color'], gl.inputs['Color']); L(nm.outputs['Vector'], gl.inputs['Normal'])
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = ior; L(nm.outputs['Vector'], fr.inputs['Normal'])
    mx = nt.nodes.new('ShaderNodeMixShader'); L(tr.outputs['BSDF'], mx.inputs[1]); L(gl.outputs['BSDF'], mx.inputs[2])
    if base is None: L(fr.outputs['Fac'], mx.inputs['Fac'])
    else:   # coated glazing: a near-constant reflectance with only a little fresnel rise (Q032 reads one tone top to bottom)
        fm = nt.nodes.new('ShaderNodeMath'); fm.operation = 'MULTIPLY_ADD'; fm.inputs[1].default_value = .35; fm.inputs[2].default_value = base
        L(fr.outputs['Fac'], fm.inputs[0]); L(fm.outputs['Value'], mx.inputs['Fac'])
    shadow_through(nt, mx, out, tint); return m

def emissive_image(name, path, strength, sat=1.0):
    m, nt, out = node_mat(name)
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path); tx.extension = 'CLIP'
    # LED pixel grid: a fine dot mask modulates the image.
    tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 90
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = .25
    nt.links.new(tc.outputs['UV'], tx.inputs['Vector']); nt.links.new(tx.outputs['Color'], mul.inputs['A']); nt.links.new(wv.outputs['Color'], mul.inputs['B'])
    nt.links.new(tc.outputs['UV'], wv.inputs['Vector'])
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = .25; gl.inputs['Color'].default_value = (.04, .04, .045, 1)
    add = nt.nodes.new('ShaderNodeAddShader')
    hs = nt.nodes.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = sat   # daylight washes the LED out (Q032)
    nt.links.new(mul.outputs['Result'], hs.inputs['Color']); nt.links.new(hs.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs['Emission'], add.inputs[0]); nt.links.new(gl.outputs['BSDF'], add.inputs[1])
    nt.links.new(add.outputs['Shader'], out.inputs['Surface']); return m


def collection(name):
    sc = bpy.context.scene
    if name not in COL:
        c = bpy.data.collections.new(name); sc.collection.children.link(c); COL[name] = c
    return COL[name]

class Builder:
    """Accumulates boxes/faces per material into one mesh per (collection, material)."""
    def __init__(s): s.parts = {}
    def bm(s, coll, mat):
        k = (coll, mat)
        if k not in s.parts: s.parts[k] = bmesh.new()
        return s.parts[k]
    def box(s, coll, mat, c, size, yaw=0., tilt=None):
        bm = s.bm(coll, mat); r = bmesh.ops.create_cube(bm, size=1)['verts']
        for v in r: v.co = Vector((v.co.x*size[0], v.co.y*size[1], v.co.z*size[2]))
        if tilt is not None: bmesh.ops.rotate(bm, verts=r, cent=(0, 0, 0), matrix=tilt)
        bmesh.ops.rotate(bm, verts=r, cent=(0, 0, 0), matrix=Matrix.Rotation(yaw, 3, 'Z'))
        bmesh.ops.translate(bm, verts=r, vec=Vector(c))
    def beam(s, coll, mat, p0, p1, w):
        d = Vector(p1)-Vector(p0); L = d.length
        if L < 1e-4: return
        bm = s.bm(coll, mat); r = bmesh.ops.create_cube(bm, size=1)['verts']
        for v in r: v.co = Vector((v.co.x*w, v.co.y*w, v.co.z*L))
        bmesh.ops.rotate(bm, verts=r, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix())
        bmesh.ops.translate(bm, verts=r, vec=Vector(p0)+d/2)
    def quad(s, coll, mat, pts, uv=None):
        bm = s.bm(coll, mat); vs = [bm.verts.new(p) for p in pts]; f = bm.faces.new(vs)
        if uv:
            lay = bm.loops.layers.uv.verify()
            for loop, u in zip(f.loops, uv): loop[lay].uv = u
    def ribbon(s, coll, mat, poly, z0, z1, closed=True):
        n = len(poly); rng = range(n if closed else n-1); u = 0.
        for i in rng:
            a, b = poly[i], poly[(i+1) % n]; L = (b-a).length
            if L < 1e-4: continue
            s.quad(coll, mat, [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)], uv=[(u, z0), (u+L, z0), (u+L, z1), (u, z1)]); u += L
    def prism(s, coll, mat, poly, z0, z1):
        bm = s.bm(coll, mat); v0 = [bm.verts.new((p.x, p.y, z0)) for p in poly]; v1 = [bm.verts.new((p.x, p.y, z1)) for p in poly]
        bm.faces.new(v0[::-1]); bm.faces.new(v1)
        for i in range(len(poly)): j = (i+1) % len(poly); bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    def cyl(s, coll, mat, p0, p1, r, segs=8, r2=None):
        d = Vector(p1)-Vector(p0); L = d.length
        if L < 1e-4: return
        bm = s.bm(coll, mat)
        v = bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r if r2 is None else r2, depth=L)['verts']
        bmesh.ops.rotate(bm, verts=v, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix())
        bmesh.ops.translate(bm, verts=v, vec=Vector(p0)+d/2)
    def sphere(s, coll, mat, c, r, sq=1.0):
        bm = s.bm(coll, mat); v = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)['verts']
        for q in v: q.co.z *= sq
        bmesh.ops.translate(bm, verts=v, vec=Vector(c))
    def finish(s):
        for (coll, mat), bm in s.parts.items():
            me = bpy.data.meshes.new(f'{coll}_{mat}'); bm.to_mesh(me); bm.free()
            for p in me.polygons: p.use_smooth = False
            o = bpy.data.objects.new(f'{coll}_{mat}', me); collection(coll).objects.link(o); me.materials.append(MAT[mat])

