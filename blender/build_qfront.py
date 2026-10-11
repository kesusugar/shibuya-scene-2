# QFRONT Photorealism Challenge - Phase 2 model (procedural, reproducible).
#
#   blender -b -P blender/build_qfront.py -- <outdir> [day|night|both] [preview|final] [save]
#
# Every dimension comes from data/measurements.json (P2-0, measured on Q032) and PLATEAU 2025 LOD2;
# see docs/DESIGN.md. Blender: metres, Z up, X east, Y north. Origin: OSM origin (35.6595, 139.7005),
# ground = crossing-side pavement.
import bpy, bmesh, math, sys, os, json, random
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]; MODE = argv[1] if len(argv) > 1 else 'day'; QUALITY = argv[2] if len(argv) > 2 else 'preview'
SAVE = 'save' in argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, 'data', 'measurements.json')))
TEX = os.path.join(ROOT, 'textures')
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- dimensions
F2, F3 = M['podium']['f2_bottom_m'], M['podium']['f2_top_m']
TOP = M['glass_storeys_top_m']; CROWN = M['crown']['top_m']; DECK = M['plateau_inner_roof_m']
LEVELS = [F2] + [F3 + 5.0 * k for k in range(7)]          # slab tops: 2F, 3F..8F, roof (40.2)
MULL = M['front_face']['mullion_pitch_m']; RAIL = M['front_face']['transom_pitch_m']
SIDE_FIN = .55; CROWN_FIN = M['crown']['fin_pitch_m']
CAVITY = .9

# ---------------------------------------------------------------- plan
def circle3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d
    uy = ((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d
    return Vector((ux, uy)), math.hypot(ax-ux, ay-uy)
P = lambda x, z: (x, -z)
fa = [P(1.04, -31.3), P(-10.75, -28.98), P(-16.64, -29.73)]
CEN, R = circle3(*fa)
a0 = math.atan2(fa[0][1]-CEN.y, fa[0][0]-CEN.x); a1 = math.atan2(fa[2][1]-CEN.y, fa[2][0]-CEN.x)
SWEEP = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
NARC = 48
ARC = [Vector((CEN.x+R*math.cos(a0+SWEEP*i/NARC), CEN.y+R*math.sin(a0+SWEEP*i/NARC))) for i in range(NARC+1)]
OUTLINE = [Vector(P(-24.84, -56.49)), Vector(P(5.08, -47.97)), Vector(P(4.44, -45.32))] + ARC + [Vector(P(-30.19, -43.09))]
KIND = ['side']*3 + ['arc']*NARC + ['side', 'side']           # kind of segment i -> i+1
def signed_area(poly): return sum(poly[i].x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*poly[i].y for i in range(len(poly)))/2
if signed_area(OUTLINE) < 0: OUTLINE.reverse(); KIND = KIND[::-1][1:] + KIND[::-1][:1]
ARC_MID = ARC[NARC//2]; ARC_N = (ARC_MID - CEN).normalized()    # outward normal at the front centre
ARC_LEN = abs(SWEEP)*R

def offset(poly, d):
    n = len(poly); out = []
    for i in range(n):
        p0, p1, p2 = poly[i-1], poly[i], poly[(i+1) % n]
        e1 = (p1-p0).normalized(); e2 = (p2-p1).normalized()
        n1 = Vector((-e1.y, e1.x)); n2 = Vector((-e2.y, e2.x))
        b = n1+n2; b = b.normalized() if b.length > 1e-6 else n1
        out.append(p1 + b*d/max(.35, b.dot(n1)))
    return out
INNER = offset(OUTLINE, CAVITY)

def segments(poly, kinds=None):
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        L = (b-a).length
        if L < 1e-4: continue
        t = (b-a)/L; n = Vector((t.y, -t.x))      # outward for CCW
        yield a, b, L, t, n, (kinds[i] if kinds else None)

# ---------------------------------------------------------------- materials
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

def glass(name, tint, transmit, rough=.02, ior=1.9):
    """Thin architectural glazing: fresnel mix of a sharp reflection and a tinted see-through."""
    m, nt, out = node_mat(name)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (tint[0]*transmit, tint[1]*transmit, tint[2]*transmit, 1)
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = rough; gl.inputs['Color'].default_value = (.9, .95, .97, 1)
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = ior    # coated panes reflect more than plain glass
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(fr.outputs['Fac'], mx.inputs['Fac']); nt.links.new(tr.outputs['BSDF'], mx.inputs[1]); nt.links.new(gl.outputs['BSDF'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m

def emissive_image(name, path, strength):
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
    nt.links.new(mul.outputs['Result'], em.inputs['Color']); nt.links.new(em.outputs['Emission'], add.inputs[0]); nt.links.new(gl.outputs['BSDF'], add.inputs[1])
    nt.links.new(add.outputs['Shader'], out.inputs['Surface']); return m

NIGHT = MODE == 'night'

def books(name):
    """Book/goods spines on shop shelving: a brick pattern of narrow, randomly tinted cells under warm light."""
    m, nt, out = node_mat(name); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = .6
    tc = nt.nodes.new('ShaderNodeTexCoord'); br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Scale'].default_value = 1.0; br.inputs['Brick Width'].default_value = .045; br.inputs['Row Height'].default_value = .32
    br.inputs['Mortar Size'].default_value = .004; br.inputs['Mortar'].default_value = (.02, .02, .02, 1)
    br.inputs['Color1'].default_value = (.45, .12, .08, 1); br.inputs['Color2'].default_value = (.12, .2, .35, 1); br.offset = .37
    vn = nt.nodes.new('ShaderNodeTexVoronoi'); vn.inputs['Scale'].default_value = 22
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'OVERLAY'; mx.inputs['Factor'].default_value = .7
    nt.links.new(tc.outputs['Object'], br.inputs['Vector']); nt.links.new(tc.outputs['Object'], vn.inputs['Vector'])
    nt.links.new(br.outputs['Color'], mx.inputs['A']); nt.links.new(vn.outputs['Color'], mx.inputs['B'])
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface']); return m
MAT = {
 'fin': principled('fin_alu', (.74, .75, .77), metal=.45, rough=.3, streaks=.25),
 'front_rail': principled('front_rail', (.52, .53, .55), metal=.6, rough=.3),
 'rail': principled('rail_alu', (.84, .85, .86), metal=.4, rough=.28, streaks=.12),
 'mullion': principled('mullion', (.55, .57, .59), metal=.8, rough=.3),
 'dark_glass': glass('glass_dark', (.45, .55, .62), .04, ior=1.6),
 'crown_glass': glass('glass_crown', (.40, .48, .55), .30, rough=.04),
 'q_bar': principled('q_bar', (.75, .05, .07), rough=.35, emit=(1, .1, .1), estr=(5 if NIGHT else 0)),
 'clear_glass': glass('glass_clear', (.85, .93, .92), .78),
 'shop_glass': glass('glass_shop', (.95, .97, .96), .88, rough=.01),
 'slab': principled('slab_edge', (.30, .30, .31), rough=.8),
 'ceiling': principled('ceiling', (.78, .77, .74), rough=.85),
 'ceil_light': principled('ceil_light', (.95, .95, .92), rough=.4, emit=(1, .93, .82), estr=(12 if NIGHT else 1.0)),
 'shop_light': principled('shop_light', (.95, .9, .8), rough=.4, emit=(1, .78, .5), estr=(14 if NIGHT else 1.0)),
 'floor': principled('floor', (.36, .34, .31), rough=.55),
 'core': principled('core_wall', (.22, .21, .2), rough=.8),
 'books': books('shop_books'),
 'shelf': principled('shelf', (.12, .12, .13), rough=.6),
 'goods': principled('goods', (.22, .19, .17), rough=.6, emit=(1, .85, .7), estr=(.6 if NIGHT else .25)),
 'steel': principled('truss_steel', (.16, .165, .17), metal=.5, rough=.4),
 'plant': principled('plant', (.72, .73, .72) if not NIGHT else (.08, .085, .09), metal=.2, rough=.5),
 'concrete': principled('concrete', (.55, .54, .52), rough=.85),
 'blind': principled('blind_wood', (.80, .58, .38), rough=.7, emit=(.95, .65, .4), estr=(.5 if NIGHT else .45)),
 'brace': principled('brace_white', (.88, .88, .88), metal=.1, rough=.35),
 'letters': principled('letters', (.95, .95, .95), rough=.3, emit=(1, 1, 1), estr=(6 if NIGHT else 0)),
 'sb_letters': principled('sb_letters', (.93, .93, .9), rough=.3, emit=(.15, 1, .45), estr=(5 if NIGHT else 0)),
 'dark_band': principled('dark_band', (.07, .07, .08), metal=.4, rough=.35),
 'tsutaya_side': principled('tsutaya_side', (.12, .12, .13), metal=.3, rough=.4),
 'lamp': principled('lamp_head', (.75, .76, .77), metal=.8, rough=.25, emit=(1, .97, .9), estr=(25 if NIGHT else 0)),
 'asphalt': principled('asphalt', (.10, .10, .105), rough=.85),
 'paving': principled('paving', (.42, .40, .38), rough=.8),
 'zebra': principled('zebra', (.82, .82, .80), rough=.6),
 'shop_in': principled('shop_interior', (.05, .045, .04), rough=.6, emit=(1, .82, .6), estr=(.03 if NIGHT else .02)),
 'context': principled('context', (.42, .42, .44), rough=.7, streaks=.2),
 'ctx_win': principled('context_windows', (.18, .2, .23), metal=.5, rough=.15, emit=(1, .85, .6), estr=(.05 if NIGHT else 0)),
 'led': emissive_image('qs_eye_main', os.path.join(TEX, 'led_main.png'), 7 if NIGHT else 2.2),
}
COL = {}
def collection(name):
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
        n = len(poly); rng = range(n if closed else n-1)
        for i in rng:
            a, b = poly[i], poly[(i+1) % n]
            if (b-a).length < 1e-4: continue
            s.quad(coll, mat, [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)])
    def prism(s, coll, mat, poly, z0, z1):
        bm = s.bm(coll, mat); v0 = [bm.verts.new((p.x, p.y, z0)) for p in poly]; v1 = [bm.verts.new((p.x, p.y, z1)) for p in poly]
        bm.faces.new(v0[::-1]); bm.faces.new(v1)
        for i in range(len(poly)): j = (i+1) % len(poly); bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    def finish(s):
        for (coll, mat), bm in s.parts.items():
            me = bpy.data.meshes.new(f'{coll}_{mat}'); bm.to_mesh(me); bm.free()
            for p in me.polygons: p.use_smooth = False
            o = bpy.data.objects.new(f'{coll}_{mat}', me); collection(coll).objects.link(o); me.materials.append(MAT[mat])

B = Builder()

def along(poly, kinds, step, want, closed=True):
    """Stations every `step` m along segments whose kind is in `want`; yields point, tangent, normal."""
    for a, b, L, t, n, k in segments(poly, kinds):
        if want and k not in want: continue
        cnt = max(1, round(L/step)) if k == 'side' else None
        if k == 'side':
            for j in range(cnt+1): yield a+t*(L*j/cnt), t, n, k
        else:
            yield a, t, n, k
def arc_stations(step, inset=0.):
    """Even stations along the front arc by arc length."""
    cnt = max(1, round(ARC_LEN/step)); out = []
    for j in range(cnt+1):
        ang = a0 + SWEEP*j/cnt; d = Vector((math.cos(ang), math.sin(ang)))
        p = CEN + d*(R-inset); t = Vector((-d.y, d.x)) * (1 if SWEEP > 0 else -1)
        out.append((p, t, d))
    return out

# ================================================================ 01 STRUCTURE / INTERIOR
INNER2 = offset(OUTLINE, CAVITY+.25)
for z in LEVELS:
    B.prism('01_STRUCTURE', 'slab', INNER2, z-.45, z)
B.prism('01_STRUCTURE', 'slab', INNER2, -.3, 0)
CORE = offset(OUTLINE, 10.5)
B.prism('01_STRUCTURE', 'core', CORE, 0, TOP)
for i, z in enumerate(LEVELS[:-1]):
    ztop = LEVELS[i+1]-.45; ceil = ztop - .05
    B.prism('08_INTERIOR', 'floor', offset(OUTLINE, CAVITY+.3), z, z+.02)
    # ceiling with linear light rows parallel to the front
    B.prism('08_INTERIOR', 'ceiling', offset(OUTLINE, CAVITY+.3), ceil-.12, ceil)
    for row in range(1, 9):
        ring = offset(OUTLINE, CAVITY+.3+row*1.15)
        for a, b, L, t, n, k in segments(ring):
            if L < 1.5: continue
            m = (a+b)/2; B.box('08_INTERIOR', 'ceil_light', (m.x, m.y, ceil-.14), (L*.85, .18, .04), math.atan2(t.y, t.x))
    # shelving / furniture rows a few metres inside the glass
    for st in arc_stations(2.4, inset=CAVITY+3.0)[1:-1]:
        p, t, d = st
        if random.random() < .75:
            h = 1.6 + random.random()*.6
            B.box('08_INTERIOR', 'shelf', (p.x, p.y, z+h/2), (1.8, .5, h), math.atan2(t.y, t.x))
            B.box('08_INTERIOR', 'goods', (p.x+d.x*.27, p.y+d.y*.27, z+h*.55), (1.6, .05, h*.7), math.atan2(t.y, t.x))

# ================================================================ 02 INNER GLASS + MULLIONS
# Front arc: dark glass 10.2-40.2, clear glass for 2F (5.3-10.2) and shop glass for 1F.
INNER_ARC = [CEN + (p-CEN).normalized()*(R-CAVITY) for p in ARC]
B.ribbon('02_INNER_GLASS', 'dark_glass', INNER_ARC, F3, TOP, closed=False)
B.ribbon('02_INNER_GLASS', 'clear_glass', INNER_ARC, F2, F3, closed=False)
SHOP_ARC = [CEN + (p-CEN).normalized()*(R-1.6) for p in ARC]
B.ribbon('06_GROUND_FLOOR', 'shop_glass', SHOP_ARC, 0, F2-.3, closed=False)
# side faces: glass behind the dense fins
side_inner = []
for a, b, L, t, n, k in segments(INNER):
    pass
for i, (a, b, L, t, n, k) in enumerate(segments(OUTLINE, KIND)):
    if k != 'side': continue
    ia, ib = a - n*CAVITY, b - n*CAVITY
    B.quad('02_INNER_GLASS', 'dark_glass', [(ia.x, ia.y, F2), (ib.x, ib.y, F2), (ib.x, ib.y, TOP), (ia.x, ia.y, TOP)])
    B.quad('06_GROUND_FLOOR', 'shop_glass', [(ia.x, ia.y, 0), (ib.x, ib.y, 0), (ib.x, ib.y, F2-.3), (ia.x, ia.y, F2-.3)])
# front mullions (1.78 m) and transom rails (3.95 m): the visible grid on the dark front
for p, t, d in arc_stations(MULL):
    q = CEN + d*(R-CAVITY+.12)
    B.box('03_OUTER_SKIN', 'mullion', (q.x, q.y, (F2+TOP)/2), (.08, .28, TOP-F2), math.atan2(t.y, t.x))
    q2 = CEN + d*(R+.05)                           # outer vertical (thin rib of the outer skin)
    B.box('03_OUTER_SKIN', 'mullion', (q2.x, q2.y, (F3+TOP)/2), (.06, .30, TOP-F3), math.atan2(t.y, t.x))
z = F3
while z <= TOP + .01:
    ring = [CEN + (p-CEN).normalized()*(R+.02) for p in ARC]
    for i in range(len(ring)-1):
        a, b = ring[i], ring[i+1]; m = (a+b)/2; t = (b-a).normalized()
        B.box('03_OUTER_SKIN', 'front_rail', (m.x, m.y, z), ((b-a).length+.02, .45, .12), math.atan2(t.y, t.x))
    z += RAIL

# ================================================================ 03 OUTER SKIN: dense side fins to the crown top
for a, b, L, t, n, k in segments(OUTLINE, KIND):
    if k != 'side': continue
    cnt = max(1, round(L/SIDE_FIN))
    for j in range(cnt+1):
        p = a + t*(L*j/cnt) + n*.18
        B.box('03_OUTER_SKIN', 'fin', (p.x, p.y, (F2+CROWN)/2), (.05, .40, CROWN-F2), math.atan2(t.y, t.x))
    for zz in [F2, F3] + [F3 + RAIL*k for k in range(1, 9)] + [CROWN-.15]:
        if zz > CROWN: continue
        m = (a+b)/2 + n*.2
        B.box('03_OUTER_SKIN', 'rail', (m.x, m.y, zz), (L+.05, .5, .14), math.atan2(t.y, t.x))

# ================================================================ 04 Q's EYE (main vision)
mv = M['main_vision']; w, h, zc = mv['width_m'], mv['height_m'], mv['centre_m']
half = (w/2)/R
bm = B.bm('04_QS_EYE', 'led'); lay = bm.loops.layers.uv.verify(); N = 16
mid_ang = a0 + SWEEP/2
for i in range(N):
    for k in range(1):
        angs = [mid_ang - half + 2*half*i/N, mid_ang - half + 2*half*(i+1)/N]
        ps = [CEN + Vector((math.cos(g), math.sin(g)))*(R-CAVITY+.35) for g in angs]
        vs = [bm.verts.new((ps[0].x, ps[0].y, zc-h/2)), bm.verts.new((ps[1].x, ps[1].y, zc-h/2)), bm.verts.new((ps[1].x, ps[1].y, zc+h/2)), bm.verts.new((ps[0].x, ps[0].y, zc+h/2))]
        f = bm.faces.new(vs)
        us = [i/N, (i+1)/N] if SWEEP < 0 else [1-i/N, 1-(i+1)/N]
        for loop, uv in zip(f.loops, [(us[0], 0), (us[1], 0), (us[1], 1), (us[0], 1)]): loop[lay].uv = uv

# ================================================================ 05 CROWN
for p, t, d in arc_stations(CROWN_FIN):
    q = CEN + d*(R+.15)
    B.box('05_CROWN', 'fin', (q.x, q.y, (TOP+CROWN)/2), (.07, .45, CROWN-TOP), math.atan2(t.y, t.x))
for zz in (TOP+.1, TOP+3.8, DECK+.2, CROWN-.2):
    ring = [CEN + (p-CEN).normalized()*(R+.2) for p in ARC]
    for i in range(len(ring)-1):
        a, b = ring[i], ring[i+1]; m = (a+b)/2; t = (b-a).normalized()
        B.box('05_CROWN', 'rail', (m.x, m.y, zz), ((b-a).length+.02, .6, .3 if zz > CROWN-1 else .18), math.atan2(t.y, t.x))
B.prism('05_CROWN', 'slab', offset(OUTLINE, 1.0), TOP-.4, TOP)
# Q032: a glazed screen sits behind the crown fins; the truss shows through it dark, the sky reflects in it
B.ribbon('05_CROWN', 'crown_glass', INNER_ARC, TOP, CROWN-.3, closed=False)
# plant enclosure (PLATEAU inner roof 48.4 m), set back
B.prism('05_CROWN', 'plant', offset(OUTLINE, 11.0), TOP, TOP+2.6)
for k in range(6):   # rooftop plant units (PLATEAU's 48.4 m returns), set well back
    c = CEN + (ARC_MID-CEN)*.35 + Vector((random.uniform(-6, 6), random.uniform(-6, 6)))
    B.box('05_CROWN', 'plant', (c.x, c.y, TOP+2.6+1.2), (random.uniform(2, 4), random.uniform(2, 4), 2.4), random.random())
# space truss between the skin and the enclosure: two chords rings, posts and diagonals
ring = offset(OUTLINE, 2.2)
posts = []
for a, b, L, t, n, k in segments(ring):
    cnt = max(1, round(L/6.0))
    for j in range(cnt): posts.append(a + t*(L*j/cnt))
for p in posts: B.beam('05_CROWN', 'steel', (p.x, p.y, TOP), (p.x, p.y, CROWN-.6), .32)
for zz in (TOP+.4, TOP+5.6, CROWN-.7):
    for i in range(len(posts)):
        a, b = posts[i], posts[(i+1) % len(posts)]
        if (b-a).length < 8: B.beam('05_CROWN', 'steel', (a.x, a.y, zz), (b.x, b.y, zz), .28)
for i in range(len(posts)):
    a, b = posts[i], posts[(i+1) % len(posts)]
    if (b-a).length > 8: continue
    if i % 2: B.beam('05_CROWN', 'steel', (a.x, a.y, TOP+.4), (b.x, b.y, TOP+5.6), .2); B.beam('05_CROWN', 'steel', (b.x, b.y, TOP+5.6), (a.x, a.y, CROWN-.7), .2)
    else: B.beam('05_CROWN', 'steel', (b.x, b.y, TOP+.4), (a.x, a.y, TOP+5.6), .2); B.beam('05_CROWN', 'steel', (a.x, a.y, TOP+5.6), (b.x, b.y, CROWN-.7), .2)
# a few big diagonal members seen through the front (Q031)
for k in range(5):
    g0 = a0 + SWEEP*(.1+.2*k); g1 = g0 + SWEEP*.12
    p0 = CEN + Vector((math.cos(g0), math.sin(g0)))*(R-2.2); p1 = CEN + Vector((math.cos(g1), math.sin(g1)))*(R-4.5)
    B.beam('05_CROWN', 'steel', (p0.x, p0.y, TOP+.5), (p1.x, p1.y, CROWN-1.0), .35)

# QFRONT lettering (Blender built-in font, DejaVu): white channel letters behind the crown fins
def text_object(body, size, extrude, coll, mat, loc, yaw, align='CENTER', rot_x=math.pi/2, font=None):
    cu = bpy.data.curves.new(body, 'FONT'); cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = 'CENTER'
    if font: cu.font = bpy.data.fonts.load(font)
    ob = bpy.data.objects.new(body, cu); collection(coll).objects.link(ob); ob.data.materials.append(MAT[mat])
    ob.location = loc; ob.rotation_euler = (rot_x, 0, yaw); return ob
lt = M['crown']['letters']; lp = ARC_MID - ARC_N*.15
yaw = math.atan2(ARC_N.y, ARC_N.x) + math.pi/2
qob = text_object('QFRONT', lt['height_m']*1.35, .25, '05_CROWN', 'letters', (lp.x, lp.y, lt['bottom_m']+lt['height_m']/2), yaw,
            font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
# the red bar through the Q (Q032 / Q031), on the left end of the word
bpy.context.view_layer.update(); qob.scale.x = lt['width_m']/max(qob.dimensions.x, 1e-3)
qx = lp - Vector((-ARC_N.y, ARC_N.x))*(lt['width_m']*.41) + ARC_N*.2
B.box('05_CROWN', 'q_bar', (qx.x, qx.y, lt['bottom_m']+lt['height_m']*.55), (1.0, .1, .2), math.atan2(ARC_N.y, ARC_N.x)+math.pi/2)

# ================================================================ 06 GROUND FLOOR + 2F
# 2F X-braces behind the glass (Q107 / Q128): white tubes, two X per ~6 m
br = arc_stations(5.6, inset=CAVITY+.6)
for i in range(len(br)-1):
    p0, p1 = br[i][0], br[i+1][0]
    B.beam('06_GROUND_FLOOR', 'brace', (p0.x, p0.y, F2), (p1.x, p1.y, F3), .45)
    B.beam('06_GROUND_FLOOR', 'brace', (p1.x, p1.y, F2), (p0.x, p0.y, F3), .45)
# 2F wood blinds, part lowered
for p, t, d in arc_stations(MULL, inset=CAVITY+.25)[:-1]:
    if random.random() < .35: continue                 # Q031/Q107: about a third of the bays have the blind up
    drop = .5 + random.random()*1.8
    B.box('06_GROUND_FLOOR', 'blind', (p.x, p.y, F3-.5-drop/2), (MULL-.12, .03, drop), math.atan2(t.y, t.x))
# dark sign band at the 2F slab, canopy over the entrance, shop interior volume
for i in range(len(ARC)-1):
    a, b = ARC[i]+(ARC[i]-CEN).normalized()*.1, ARC[i+1]+(ARC[i+1]-CEN).normalized()*.1; m = (a+b)/2; t = (b-a).normalized()
    B.box('06_GROUND_FLOOR', 'dark_band', (m.x, m.y, F2-.15), ((b-a).length+.02, .5, .9), math.atan2(t.y, t.x))
cs = ARC_MID + ARC_N*1.2
B.box('06_GROUND_FLOOR', 'rail', (cs.x, cs.y, M['podium']['canopy_m']+.6), (15.0, 2.6, .35), math.atan2(ARC_N.y, ARC_N.x)+math.pi/2)
for s in (-1, 1):
    tv = Vector((-ARC_N.y, ARC_N.x))*s*7.0; q = ARC_MID + ARC_N*2.3 + tv
    B.box('06_GROUND_FLOOR', 'rail', (q.x, q.y, (M['podium']['canopy_m']+.6)/2), (.18, .18, M['podium']['canopy_m']+.6), 0)
# 1F shop interior: floor, back wall 6 m in, ceiling with downlights, display tables and shelving
B.prism('06_GROUND_FLOOR', 'floor', offset(OUTLINE, 1.7), .0, .03)
B.ribbon('06_GROUND_FLOOR', 'shop_in', offset(OUTLINE, 7.5), 0, F2-.5)
B.prism('06_GROUND_FLOOR', 'shelf', offset(OUTLINE, 1.7), F2-.75, F2-.6)   # dark ceiling: the light comes from the downlights
for row in range(1, 5):
    for p, t, d in arc_stations(1.8, inset=1.7+row*1.3):
        B.box('06_GROUND_FLOOR', 'shop_light', (p.x, p.y, F2-.78), (.18, .18, .03), math.atan2(t.y, t.x))
# TSUTAYA 1F (Q016 / Q107): low display tables near the glass, rows of tall book and media shelving behind
for p, t, d in arc_stations(2.6, inset=3.2)[1:-1]:
    if random.random() < .6:
        B.box('06_GROUND_FLOOR', 'shelf', (p.x, p.y, .45), (1.6, .9, .9), math.atan2(t.y, t.x))
        B.box('06_GROUND_FLOOR', 'books', (p.x, p.y, .93), (1.5, .8, .06), math.atan2(t.y, t.x))
for inset in (4.6, 5.8, 7.0):
    for p, t, d in arc_stations(1.9, inset=inset)[1:-1]:
        if random.random() < .15: continue
        h = 1.6 + random.random()*.6
        B.box('06_GROUND_FLOOR', 'shelf', (p.x, p.y, h/2), (1.75, .45, h), math.atan2(t.y, t.x))
        B.box('06_GROUND_FLOOR', 'books', (p.x+d.x*.24, p.y+d.y*.24, h*.5), (1.65, .02, h*.85), math.atan2(t.y, t.x))
# signage: STARBUCKS COFFEE (2F, left of centre) and TSUTAYA (band, right of centre) - text in a stock font
tang = Vector((-ARC_N.y, ARC_N.x))
sb = ARC_MID + ARC_N*.25 - tang*1.0
text_object('STARBUCKS COFFEE', 1.0, .05, '06_GROUND_FLOOR', 'sb_letters', (sb.x, sb.y, M['podium']['starbucks_sign_m']), yaw, font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
ts = ARC_MID + ARC_N*.4 + tang*5.8
text_object('TSUTAYA', 1.0, .08, '06_GROUND_FLOOR', 'letters', (ts.x, ts.y, M['podium']['tsutaya_band_m']-.1), yaw, font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
# east face: tall vertical TSUTAYA letters (dark), on the side segment nearest the arc start
for a, b, L, t, n, k in segments(OUTLINE, KIND):
    if k == 'side' and (a - Vector(P(4.44, -45.32))).length < .1 or (b - Vector(P(4.44, -45.32))).length < .1 and k == 'side':
        pass
east_a, east_b = Vector(P(4.44, -45.32)), ARC[0] if (ARC[0]-Vector(P(1.04, -31.3))).length < .5 else ARC[-1]
et = (east_b-east_a).normalized(); en = Vector((et.y, -et.x))
if en.x < 0: en = -en
# one text, rotated to read top-to-bottom (Q118, Q032): local X -> down, local Z -> out of the face
tob = text_object('TSUTAYA', 3.4, .15, '07_FIXTURES', 'tsutaya_side', (0, 0, 0), 0, align='CENTER')
yv = Vector((-en.y, en.x, 0)); basis = Matrix(((0, yv.x, en.x), (0, yv.y, en.y), (-1, 0, 0)))
pc = (east_a+east_b)/2 + en*.55
tob.matrix_world = Matrix.Translation((pc.x, pc.y, 25.0)) @ basis.to_4x4()

# ================================================================ 07 FIXTURES: floodlight arms at the arc ends
for end, (z0, z1) in ((ARC[0], M['floodlights']['right_m']), (ARC[-1], M['floodlights']['left_m'])):
    d = (end-CEN).normalized(); side = Vector((-d.y, d.x)); side = side if (end-ARC_MID).dot(side) > 0 else -side
    for k in range(7):
        zz = z0 + (z1-z0)*k/6; base = end + d*.4 + side*(k*.35); tip = base + d*1.1
        B.beam('07_FIXTURES', 'rail', (base.x, base.y, zz), (tip.x, tip.y, zz+.3), .12)
        B.box('07_FIXTURES', 'lamp', (tip.x, tip.y, zz+.3), (.45, .45, .35))
    if NIGHT:
        for k in range(3):
            zz = z0 + (z1-z0)*k/2; tip = end + d*1.6 + side*1.8
            L = bpy.data.lights.new(f'flood{k}', 'SPOT'); L.energy = 3000; L.spot_size = math.radians(45); L.spot_blend = .6; L.color = (1, .95, .88)
            o = bpy.data.objects.new(f'flood{k}', L); collection('07_FIXTURES').objects.link(o)
            o.location = (tip.x, tip.y, zz); aim = Vector((end.x - side.x*12, end.y - side.y*12, zz-22)) - o.location
            o.rotation_euler = aim.to_track_quat('-Z', 'Y').to_euler()

# ================================================================ 09 CONTEXT: pavement, crossing, neighbours
B.prism('09_CONTEXT', 'asphalt', [Vector((-160, -120)), Vector((160, -120)), Vector((160, 160)), Vector((-160, 160))], -.3, -.02)
B.prism('09_CONTEXT', 'paving', offset(OUTLINE, -6.0), -.3, .15)
# zebra stripes across the front of QFRONT (approx. OSM crossing way/1157451161 and neighbours)
fwd = ARC_N; side = Vector((-fwd.y, fwd.x))
for j in range(-14, 15):
    c = ARC_MID + fwd*14 + side*(j*.9)
    B.box('09_CONTEXT', 'zebra', (c.x, c.y, -.015), (.45, 4.0, .02), math.atan2(side.y, side.x))
for j in range(-10, 11):
    c = ARC_MID + fwd*34 + side*(j*.9 + 6)
    B.box('09_CONTEXT', 'zebra', (c.x, c.y, -.015), (.45, 4.0, .02), math.atan2(side.y, side.x))
random.seed(11)
# Across the crossing, behind the camera: the station-side blocks the front glass reflects (Q032 shows them dark in it).
far = ARC_MID + ARC_N*135; ftan = Vector((-ARC_N.y, ARC_N.x)); fyaw = math.atan2(ftan.y, ftan.x)
for k, (off, w_, h_) in enumerate([(-50, 40, 28), (-8, 36, 42), (32, 44, 34), (75, 40, 60)]):
    c = far + ftan*off
    B.box('09_CONTEXT', 'context', (c.x, c.y, h_/2), (w_, 20, h_), fyaw)
    for zz in range(3, int(h_)-2, 4): B.box('09_CONTEXT', 'ctx_win', (c.x, c.y, zz+1), (w_+.06, 20.06, 1.7), fyaw)
CTX_COLS = [(.55, .53, .5), (.68, .66, .62), (.38, .4, .42), (.72, .7, .66), (.47, .45, .43)]
for k, (cx, cy, w_, d_, h_, yaw_) in enumerate([(-45, 30, 16, 24, 26, .1), (-48, 55, 18, 18, 38, .1), (22, 55, 20, 24, 30, -.2), (30, 82, 26, 22, 22, -.2),
                                  (-15, 80, 40, 18, 32, 0), (-80, 10, 30, 30, 35, .2), (60, 20, 30, 40, 34, -.3), (-30, -40, 22, 18, 30, .3), (35, -35, 30, 25, 35, -.4)]):
    mname = f'ctx{k%5}'
    if mname not in MAT: MAT[mname] = principled(mname, CTX_COLS[k % 5], rough=.75, streaks=.25)
    B.box('09_CONTEXT', mname, (cx, cy, h_/2), (w_, d_, h_), yaw_)
    R2 = Matrix.Rotation(yaw_, 3, 'Z')
    for zz in range(4, int(h_)-1, 4):                    # ribbon windows with mullions on all four faces
        B.box('09_CONTEXT', 'ctx_win', (cx, cy, zz+1.2), (w_+.08, d_+.08, 1.9), yaw_)
        for side, (L_, ax) in enumerate(((w_, Vector((1, 0, 0))), (d_, Vector((0, 1, 0))))):
            nrm = Vector((0, 1, 0)) if side == 0 else Vector((1, 0, 0)); half = (d_ if side == 0 else w_)/2 + .08
            for sgn in (-1, 1):
                for u in [x*1.6 - L_/2 for x in range(int(L_/1.6)+1)]:
                    p = Vector((cx, cy, zz+1.2)) + R2 @ (ax*u + nrm*sgn*half)
                    B.box('09_CONTEXT', 'mullion', p, (.08, .08, 1.9), yaw_)
    for r in range(random.randint(1, 3)):               # roof plant
        B.box('09_CONTEXT', 'plant', (cx+random.uniform(-w_/4, w_/4), cy+random.uniform(-d_/4, d_/4), h_+1), (random.uniform(2, 5), random.uniform(2, 5), 2), yaw_)

B.finish()

# ================================================================ world, camera, render
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
prev = QUALITY == 'preview'
sc.cycles.samples = 64 if prev else 256; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.transparent_max_bounces = 16; sc.cycles.glossy_bounces = 4
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.world = bpy.data.worlds.new('sky'); sc.world.use_nodes = True; nt = sc.world.node_tree
sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'
bg = nt.nodes['Background']; nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
if NIGHT:
    # blue hour (Q031 dusk): a plain deep-blue dome; the city supplies the rest of the light
    nt.links.remove(bg.inputs['Color'].links[0]); bg.inputs['Color'].default_value = (.012, .035, .16, 1); bg.inputs['Strength'].default_value = 1.0
    sc.view_settings.exposure = .3
else:
    # Q032: 2018-10-30 10:25 JST -> sun azimuth ~152 deg (from north, clockwise), elevation ~38 deg
    sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(90 - 152 + 180); bg.inputs['Strength'].default_value = .32; sc.view_settings.exposure = -.2
    sky.air_density = .7; sky.dust_density = .15; sky.ozone_density = 4.0; sky.sun_disc = False
    # Q032 was shot with a deep, near-polarised blue sky. Only camera rays see the deeper tint; the scene is still lit by the plain sky.
    lp_ = nt.nodes.new('ShaderNodeLightPath'); deep = nt.nodes.new('ShaderNodeMix'); deep.data_type = 'RGBA'; deep.blend_type = 'MULTIPLY'
    deep.inputs['B'].default_value = (.26, .40, .78, 1)
    nt.links.new(lp_.outputs['Is Camera Ray'], deep.inputs['Factor']); nt.links.new(sky.outputs['Color'], deep.inputs['A']); nt.links.new(deep.outputs['Result'], bg.inputs['Color'])
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 5.5; sun.angle = math.radians(.6)
    so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
    az = math.radians(152); el = math.radians(38)
    dirv = Vector((math.sin(az)*math.cos(el), math.cos(az)*math.cos(el), math.sin(el)))   # towards the sun
    so.rotation_euler = (-dirv).to_track_quat('-Z', 'Y').to_euler()

def camera_q032(name, D=90., lateral=1.0, res=(640, 875)):
    cam = bpy.data.cameras.new(name); co = bpy.data.objects.new(name, cam); sc.collection.objects.link(co)
    tang = Vector((-ARC_N.y, ARC_N.x))
    pos = ARC_MID + ARC_N*D + tang*lateral
    co.location = (pos.x, pos.y, 1.6)
    look = Vector((-ARC_N.x, -ARC_N.y, 0))
    co.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    W_, H_ = res; sc.render.resolution_x, sc.render.resolution_y = W_, H_
    # Q032 is perspective-corrected: level camera, lens shift. 25.4 px/m at the front face, ground at row 1565/1749.
    fpx = 25.4*D*(H_/1749); cam.sensor_fit = 'VERTICAL'; cam.angle_y = 2*math.atan((H_/2)/fpx)
    y_ground = 1565*(H_/1749); y_pp = y_ground - 25.4*(H_/1749)*1.6
    cam.shift_y = (y_pp - H_/2)/H_ * (H_/max(W_, H_)) * (max(W_, H_)/H_) if H_ >= W_ else (y_pp - H_/2)/W_
    cam.clip_end = 2000; sc.camera = co; return co

VIEW = next((a for a in argv[3:] if a.startswith('view=')), 'view=q032')[5:]
def camera_look(name, pos, target, lens, res):
    cam = bpy.data.cameras.new(name); co = bpy.data.objects.new(name, cam); sc.collection.objects.link(co)
    co.location = pos; co.rotation_euler = (Vector(target)-Vector(pos)).to_track_quat('-Z', 'Y').to_euler(); cam.lens = lens; cam.clip_end = 2000
    sc.render.resolution_x, sc.render.resolution_y = res; sc.camera = co
scale = 1 if prev else 2
TANG = Vector((-ARC_N.y, ARC_N.x))
if VIEW == 'q032':
    camera_q032('cam_q032', res=(640, 875) if prev else (1280, 1749))
elif VIEW == 'q107':   # three-quarter street view from the south-west corner of the crossing (Q107-like)
    d = (ARC_N*math.cos(math.radians(-28)) + TANG*math.sin(math.radians(-28))); p = ARC_MID + d*62
    camera_look('cam_q107', (p.x, p.y, 1.6), (ARC_MID.x, ARC_MID.y, 21), 22, (800*scale//1, 533*scale//1))
elif VIEW == 'close':  # podium and lower screen from the kerb (Q016-like)
    p = ARC_MID + ARC_N*30 - TANG*3
    camera_look('cam_close', (p.x, p.y, 1.6), (ARC_MID.x, ARC_MID.y, 13), 45, (800*scale, 533*scale))
elif VIEW == 'crown':  # crown and lettering, long lens from across the crossing
    p = ARC_MID + ARC_N*95 + TANG*8
    camera_look('cam_crown', (p.x, p.y, 20), (ARC_MID.x, ARC_MID.y, 45), 135, (800*scale, 533*scale))
os.makedirs(OUT, exist_ok=True)
sc.render.filepath = os.path.join(OUT, f'{MODE}_{VIEW}_{QUALITY}.png')
if SAVE: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'qfront.blend'))
if 'norender' not in argv: bpy.ops.render.render(write_still=True)
tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in sc.objects if o.type == 'MESH')
print(f'RENDERED {MODE} {QUALITY} arcR={R:.2f} tris={tris}')
