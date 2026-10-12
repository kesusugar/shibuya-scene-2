# MAGNET by SHIBUYA109 - G3 v1 model (procedural, reproducible), built the QFRONT way.
#
#   blender -b -P blender/build_magnet.py -- <outdir> [day|night] [preview|final] [view=m027|sw|south|roof] [era=2025|none]
#           [clay] [save] [norender] [border=x0,y0,x1,y1 zoom=N tag=name]
#
# Plan and roof heights: PLATEAU 2025 LOD2 (data/magnet_plateau_lod2.json). Facade elevations: back-projected on the
# 2025-09-01 photo M027 with the fitted camera (data/camera_m027_fit.json). See data/measurements.json.
# Axes: X=east, Y=north, Z=up, metres above the south-west pavement (elevation 14.561 m).
# The 2025 signs, ads and screens are a separate era layer (data/signage_<era>.json -> collection 08_SIGNS_<era>).
import bpy, bmesh, math, sys, os, json, random
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matlib
from matlib import node_mat, principled, panel_glass, emissive_image, shadow_through, Builder, MAT

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]; MODE = argv[1] if len(argv) > 1 else 'day'; QUALITY = argv[2] if len(argv) > 2 else 'preview'
opt = lambda k, d: next((a[len(k)+1:] for a in argv if a.startswith(k + '=')), d)
VIEW = opt('view', 'm027'); ERA = opt('era', '2025')
NIGHT = MODE == 'night'; matlib.NIGHT = NIGHT
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda f: os.path.join(ROOT, 'data', f)
M = json.load(open(D('measurements.json'))); LOD = json.load(open(D('magnet_plateau_lod2.json'))); HGT = M['heights']
TEX = os.path.join(ROOT, 'textures')
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
V2 = lambda p: Vector((p[0], p[1]))

# ---------------------------------------------------------------- plan (PLATEAU roof polygons, by height)
def roof_polys(h, tol=.02):
    return [[V2(p) for p in s[:-1]] for s in LOD['RoofSurface'] if abs(sum(p[2] for p in s)/len(s) - h) < tol]
TOWER = roof_polys(40.37)[0]                    # main glass tower (east/diagonal block)
TOWER_FW = roof_polys(40.33)[0]                 # tower front strip at the south-west
STEP_A = roof_polys(36.06)[0]; STEP_B = roof_polys(36.73)[0]
WING = roof_polys(33.1, .1)[0]                  # white west wing (deck polygon, notched round the drum)
ANNEX = [p for p in roof_polys(31.44) if max(v.y for v in p) > 60][0]
NE = roof_polys(35.99)[0] + []; NE2 = roof_polys(34.41)[0]
EIRAKU = [V2(p) for p in M['eiraku']['poly']]
GBOX = [V2(p) for p in M['glass_box']['poly']]   # v2: lower glass block from the photos (not in PLATEAU)

def area(poly): return sum(poly[i].x*poly[(i+1) % len(poly)].y - poly[(i+1) % len(poly)].x*poly[i].y for i in range(len(poly)))/2
def ccw(poly): return poly if area(poly) > 0 else poly[::-1]
TOWER, TOWER_FW, STEP_A, STEP_B, WING, ANNEX, NE, NE2, EIRAKU, GBOX = map(ccw, (TOWER, TOWER_FW, STEP_A, STEP_B, WING, ANNEX, NE, NE2, EIRAKU, GBOX))
def edges(poly):
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]; L = (b-a).length
        if L > .05: t = (b-a)/L; yield a, b, L, t, Vector((t.y, -t.x))    # outward normal for CCW

# ---------------------------------------------------------------- materials
def mat(name, m): MAT[name] = m; return m
def panel_white(name, col, pw, ph, joint=.012, rough=.38, dirt=.08):
    """Metal/ceramic cladding panels pw x ph m (UVs in metres): dark joints, slight per-panel tone, rain streaks."""
    m, nt, out = node_mat(name); L = nt.links.new; b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = rough; tc = nt.nodes.new('ShaderNodeTexCoord')
    br = nt.nodes.new('ShaderNodeTexBrick'); br.offset = 0; br.inputs['Scale'].default_value = 1
    br.inputs['Brick Width'].default_value = pw; br.inputs['Row Height'].default_value = ph; br.inputs['Mortar Size'].default_value = joint
    br.inputs['Mortar'].default_value = (col[0]*.35, col[1]*.35, col[2]*.36, 1)
    br.inputs['Color1'].default_value = (*col, 1); br.inputs['Color2'].default_value = (col[0]*.95, col[1]*.95, col[2]*.94, 1)
    L(tc.outputs['UV'], br.inputs['Vector'])
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (3, .3, 1); L(tc.outputs['UV'], mp.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.6; nz.inputs['Detail'].default_value = 6; L(mp.outputs['Vector'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = .45; mr.inputs['From Max'].default_value = .8
    mr.inputs['To Min'].default_value = 0; mr.inputs['To Max'].default_value = dirt; L(nz.outputs['Fac'], mr.inputs['Value'])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.inputs['B'].default_value = (.55, .53, .5, 1); L(mr.outputs['Result'], mx.inputs['Factor']); L(br.outputs['Color'], mx.inputs['A'])
    L(mx.outputs['Result'], b.inputs['Base Color']); L(b.outputs['BSDF'], out.inputs['Surface']); return m

def textured(name, path, rough=.45, emit=0., ext='CLIP', alpha=False):
    m, nt, out = node_mat(name); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = rough
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path); tx.extension = ext
    tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['UV'], tx.inputs['Vector']); nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    if alpha: nt.links.new(tx.outputs['Alpha'], b.inputs['Alpha']); m.blend_method = 'HASHED' if hasattr(m, 'blend_method') else None
    if emit: nt.links.new(tx.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface']); return m

mat('white_panel', panel_white('white_panel', (.80, .80, .78), M['west_face']['panel_w_m'], M['west_face']['panel_h_m']))
mat('drum_panel', panel_white('drum_panel', (.82, .82, .80), 1.0, M['west_face']['panel_h_m'], dirt=.05))
mat('eiraku_wall', panel_white('eiraku_wall', (.74, .74, .72), .6, .45, joint=.006, dirt=.12))
mat('ribbon_glass', panel_glass('ribbon_glass', (.25, .28, .32), .35 if not NIGHT else .2, 1.6, 1.9, 1.0, base=.25))
def tint_reflection(m, rgb):
    nt = m.node_tree; gl = next(n for n in nt.nodes if n.type == 'BSDF_GLOSSY'); src = gl.inputs['Color'].links[0].from_socket
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
    nt.links.new(src, mx.inputs[6]); mx.inputs[7].default_value = (*rgb, 1); nt.links.new(mx.outputs[2], gl.inputs['Color']); return m
mat('tower_glass', panel_glass('tower_glass', (.18, .24, .34), .22, 2.2, M['tower']['pane_w_m'], M['tower']['pane_h_m'], wobble=.05, base=.3))
tint_reflection(MAT['tower_glass'], (.14, .24, .52))   # v2: M027 glass reads 31,49,80
mat('shop_glass', panel_glass('shop_glass', (.6, .62, .62), .75, 1.5, 1.8, 3.0, base=.06))
mat('lookout_glass', panel_glass('lookout_glass', (.7, .75, .78), .8, 1.5, 1.2, 1.1, base=.08))
mat('mullion', principled('mullion', (.16, .17, .19), metal=.7, rough=.35))
mat('tower_mullion', principled('tower_mullion', (.42, .44, .47), metal=.85, rough=.3))   # M027/M002: light silver grid on the tower
mat('steel', principled('steel', (.55, .56, .57), metal=.8, rough=.4))
mat('steel_dark', principled('steel_dark', (.2, .2, .21), metal=.6, rough=.45))
mat('box_grey', principled('box_grey', (.22, .225, .235), metal=.25, rough=.5, streaks=.25))
mat('roof', principled('roof', (.42, .42, .41), rough=.85, streaks=.2))
mat('deck_wood', principled('deck_wood', (.36, .27, .2), rough=.7))
mat('plant', principled('plant', (.72, .73, .72), metal=.1, rough=.5, streaks=.2))
mat('canopy', principled('canopy', (.86, .86, .85), metal=.2, rough=.3))
mat('pavement', principled('pavement', (.24, .235, .225), rough=.9, streaks=.3))
mat('asphalt', principled('asphalt', (.07, .07, .075), rough=.9))
mat('soffit', principled('soffit', (.9, .88, .82), emit=(1, .9, .75), estr=4.0 if NIGHT else .6))
warm = (1.0, .78, .5)
mat('interior', principled('interior', (.35, .32, .28), rough=.8, emit=warm, estr=3.5 if NIGHT else .12))
mat('lookout_led', principled('lookout_led', (.5, .3, .9), emit=(.55, .3, 1.0), estr=12 if NIGHT else 0.))

B = Builder()

def wall(coll, m, a, b, z0, z1, n=None, off=0.):
    """Vertical quad from plan point a to b, UVs in metres (u along, v = z)."""
    if n is not None: a, b = a + n*off, b + n*off
    L = (b-a).length
    B.quad(coll, m, [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)], uv=[(0, z0), (L, z0), (L, z1), (0, z1)])

def cap(coll, m, poly, z, down=False):
    bm = B.bm(coll, m); vs = [bm.verts.new((p.x, p.y, z)) for p in (poly[::-1] if down else poly)]; f = bm.faces.new(vs)
    lay = bm.loops.layers.uv.verify()
    for lp in f.loops: lp[lay].uv = (lp.vert.co.x, lp.vert.co.y)

def inside(pt, poly):
    c = False
    for i in range(len(poly)):
        a, b = poly[i], poly[i-1]
        if (a.y > pt.y) != (b.y > pt.y) and pt.x < (b.x-a.x)*(pt.y-a.y)/(b.y-a.y) + a.x: c = not c
    return c

HEIGHT = {}   # id(poly) -> roof height, filled below
def exterior(a, b, n, others):
    """True when the edge's outside is open air (not covered by another mass)."""
    m_ = (a+b)/2 + n*.4
    return not any(inside(m_, o) for o in others)
def neighbour_h(a, b, n, others):
    """Height of the tallest other mass just outside the edge (0 if none): walls start above it."""
    m_ = (a+b)/2 + n*.4
    return max([HEIGHT.get(id(o), 0) for o in others if inside(m_, o)] + [0])

DRUM_C = V2(M['drum']['centre']); DRUM_R = M['drum']['r']
WF = M['west_face']; RIB = WF['ribbons_m']; WALL_TOP = HGT['west_wall_top_m']
ALL = [TOWER, TOWER_FW, STEP_A, STEP_B, WING, ANNEX, NE, NE2, EIRAKU, GBOX]
for poly_, h_ in ((TOWER, HGT['tower_parapetTop_m']), (TOWER_FW, HGT['tower_parapetTop_m']), (STEP_A, HGT['tower_step_roofs_m'][0]),
                  (STEP_B, HGT['tower_step_roofs_m'][1]), (WING, HGT['west_wall_top_m']), (ANNEX, HGT['north_annex_roof_m']),
                  (NE, 35.99), (NE2, 34.41), (EIRAKU, HGT['eiraku_roof_m']), (GBOX, M['glass_box']['top_m'])): HEIGHT[id(poly_)] = h_
HEIGHT[id(TOWER_FW)] = HGT['tower_front_west_roof_m'] + .4

# ---------------------------------------------------------------- 01 west wing: white panels, ribbon windows, shopfront
def clad_white(coll, a, b, n, L, z0, z1, ribbons, punched=False):
    """White cladding with ribbon (or punched) windows; the windows sit 0.12 m behind the panel face."""
    cuts = sorted(r for r in ribbons if r[1] > z0 and r[0] < z1)
    z = z0
    for r0, r1 in cuts:
        if r0 > z: wall(coll, 'white_panel', a, b, z, r0, n)
        if punched:
            k = max(1, int(L // 3.2)); w = min(2.4, L/k - .6)
            for i in range(k):
                c = a + (b-a)*((i+.5)/k); t = (b-a).normalized(); p0, p1 = c - t*w/2, c + t*w/2
                wall(coll, 'ribbon_glass', p0, p1, r0, r1, n, -.12); wall(coll, 'interior', p0, p1, r0, r1, n, -.9)
            # panel strips between the punched windows
            edges_ = [a] + sum(([a + (b-a)*((i+.5)/k) - (b-a).normalized()*w/2, a + (b-a)*((i+.5)/k) + (b-a).normalized()*w/2] for i in range(k)), []) + [b]
            for j in range(0, len(edges_), 2): wall(coll, 'white_panel', edges_[j], edges_[j+1], r0, r1, n)
        else:
            wall(coll, 'ribbon_glass', a, b, r0, r1, n, -.12); wall(coll, 'interior', a, b, r0, r1, n, -1.2)
            for zz in (r0, r1): B.quad(coll, 'mullion', [(a+n*0).to_3d() + Vector((0, 0, zz)), (b).to_3d() + Vector((0, 0, zz)),
                                                         (b - n*.12).to_3d() + Vector((0, 0, zz)), (a - n*.12).to_3d() + Vector((0, 0, zz))])
        z = r1
    if z < z1: wall(coll, 'white_panel', a, b, z, z1, n)

for a, b, L, t, n in edges(WING):
    if not exterior(a, b, n, [o for o in ALL if o is not WING]): continue
    if (a-DRUM_C).length < DRUM_R + .9 and (b-DRUM_C).length < DRUM_R + .9: continue     # hidden inside the drum
    chamfer = abs(t.dot(Vector((.707, -.707)))) > .9 and (a.y < 22 or b.y < 22)
    zbot = WF['storefront_top_m']
    clad_white('01_WEST_WING', a, b, n, L, zbot, WALL_TOP, RIB + ([[13.1, 14.1]] if chamfer else []), punched=chamfer)
    # shopfront: glazing set 0.6 m back under a soffit, white stall riser at the slab line
    wall('01_WEST_WING', 'shop_glass', a, b, 0, zbot - .9, n, -.6); wall('01_WEST_WING', 'interior', a, b, 0, zbot - .9, n, -3.0)
    wall('01_WEST_WING', 'white_panel', a, b, zbot - .9, zbot, n)
    B.quad('01_WEST_WING', 'soffit', [(a.x, a.y, zbot-.9), (b.x, b.y, zbot-.9), (b.x-n.x*.6, b.y-n.y*.6, zbot-.9), (a.x-n.x*.6, a.y-n.y*.6, zbot-.9)])
    # mullions in the shop glazing every 1.8 m
    for k in range(int(L // 1.8) + 1):
        p = a + t*min(L, k*1.8) - n*.55; B.box('01_WEST_WING', 'mullion', (p.x, p.y, (zbot-.9)/2), (.08, .08, zbot-.9), yaw=math.atan2(t.y, t.x))
    # roof-edge truss (M027/M001: a steel lattice frame standing on the wall top, 3.3 m)
    if not chamfer:   # M027: the truss runs along the west face only, not over the chamfer
        zt0, zt1 = WALL_TOP, WALL_TOP + M['rooftop']['truss_h']; k = max(1, int(L // 2.4))
        for zz in (zt0 + .1, zt1): B.beam('06_ROOFTOP', 'steel', (a.x, a.y, zz), (b.x, b.y, zz), .14)
        for i in range(k + 1):
            p = a + t*(L*i/k); B.beam('06_ROOFTOP', 'steel', (p.x, p.y, zt0), (p.x, p.y, zt1), .12)
            if i < k:
                q = a + t*(L*(i+1)/k); B.beam('06_ROOFTOP', 'steel', (p.x, p.y, zt0) if i % 2 else (p.x, p.y, zt1), (q.x, q.y, zt1) if i % 2 else (q.x, q.y, zt0), .07)
cap('01_WEST_WING', 'roof', WING, WALL_TOP + .05)
cap('01_WEST_WING', 'roof', WING, 0.02, down=True)
# west face canopy over the pavement (M001/M027), and the rooftop deck seating (M020) on the wing roof
for a, b, L, t, n in edges(WING):
    if L > 30:   # the long west face
        za = M['podium']['canopy_z']
        B.box('05_PODIUM', 'canopy', ((a.x+b.x)/2 + n.x*.9, (a.y+b.y)/2 + n.y*.9, za), (L*.92, 1.8, .22), yaw=math.atan2(t.y, t.x))
        WEST_A, WEST_B, WEST_T, WEST_N = a, b, t, n
c0 = Vector((36.5, 40.0))
for k in range(6):   # stepped bleacher seating on the deck, facing south-west (MAG7, M020)
    B.box('06_ROOFTOP', 'deck_wood', (c0.x + .2*k, c0.y + 1.1*k, WALL_TOP + .25 + .35*k), (6.5, 1.0, .5 + .7*k), yaw=math.radians(78))
for p in ((33.0, 45.0), (35.0, 52.0), (38.0, 58.0)):   # v2: clear of the glass block
    B.box('06_ROOFTOP', 'plant', (p[0], p[1], WALL_TOP + 1.0), (3.0, 2.2, 2.0))

# ---------------------------------------------------------------- 02 drum: white cylinder, dark band, glazed lookout
NS = 48; ZD0, ZD1 = M['drum']['z0'], M['drum']['top_m']
def ring(r, z0, z1, m, coll='02_DRUM', a0=0, a1=360, uvh=None):
    for i in range(NS):
        u0 = a0 + (a1-a0)*i/NS; u1 = a0 + (a1-a0)*(i+1)/NS
        p0 = DRUM_C + Vector((math.cos(math.radians(u0)), math.sin(math.radians(u0))))*r
        p1 = DRUM_C + Vector((math.cos(math.radians(u1)), math.sin(math.radians(u1))))*r
        arc = math.radians(a1-a0)*r
        B.quad(coll, m, [(p0.x, p0.y, z0), (p1.x, p1.y, z0), (p1.x, p1.y, z1), (p0.x, p0.y, z1)],
               uv=[(arc*i/NS, z0), (arc*(i+1)/NS, z0), (arc*(i+1)/NS, z1), (arc*i/NS, z1)] if uvh is None else
               [(i/NS, 0), ((i+1)/NS, 0), ((i+1)/NS, 1), (i/NS, 1)])
band = (27.0, 28.1)     # M027: one dark glazed band just under the drum top
ring(DRUM_R, ZD0, band[0], 'drum_panel'); ring(DRUM_R - .1, band[0], band[1], 'ribbon_glass'); ring(DRUM_R - .9, band[0], band[1], 'interior')
ring(DRUM_R, band[1], ZD1, 'drum_panel')
for zz in (ZD0, ZD1):
    poly = [DRUM_C + Vector((math.cos(2*math.pi*i/NS), math.sin(2*math.pi*i/NS)))*DRUM_R for i in range(NS)]
    cap('02_DRUM', 'roof', poly, zz, down=(zz == ZD0))
# lookout: octagonal glazed room (2.7 m) with a dark frame, on the drum top
R2 = M['drum']['lookout_r']; ZL = M['drum']['lookout_top_m']
oct_ = [DRUM_C + Vector((math.cos(math.radians(22.5 + 45*i)), math.sin(math.radians(22.5 + 45*i))))*R2 for i in range(8)]
for i in range(8):
    a, b = oct_[i], oct_[(i+1) % 8]; t = (b-a).normalized(); n = Vector((t.y, -t.x))
    wall('02_DRUM', 'lookout_glass', a, b, ZD1 + .4, ZL - .35, n)
    B.beam('02_DRUM', 'steel_dark', (a.x, a.y, ZD1), (a.x, a.y, ZL), .1)
    for zz in (ZD1 + .4, ZL - .35, ZL): B.beam('02_DRUM', 'steel_dark', (a.x, a.y, zz), (b.x, b.y, zz), .1)
    B.quad('02_DRUM', 'lookout_led', [(a.x, a.y, ZL - .3), (b.x, b.y, ZL - .3), (b.x, b.y, ZL - .2), (a.x, a.y, ZL - .2)])
cap('02_DRUM', 'steel_dark', oct_, ZL)

# ---------------------------------------------------------------- 03 glass tower: curtain wall with mullion grid
PW, PH = M['tower']['pane_w_m'], M['tower']['pane_h_m']; ZG0 = M['tower']['glass_bottom_m']
def curtain(poly, ztop, others, zbot=ZG0):
    for a, b, L, t, n in edges(poly):
        z_n = neighbour_h(a, b, n, others)
        if z_n >= ztop - .05: continue
        zb = max(zbot, z_n)
        wall('03_TOWER', 'tower_glass', a, b, zb, ztop, n); wall('03_TOWER', 'interior', a, b, zb, ztop, n, -1.5)
        k = max(1, round(L / PW)); yaw = math.atan2(t.y, t.x)
        for i in range(k + 1):
            p = a + t*(L*i/k) + n*.05; B.box('03_TOWER', 'tower_mullion', (p.x, p.y, (zb+ztop)/2), (.07, .1, ztop-zb), yaw=yaw)
        z = zbot
        while z < zb - 1e-3: z += PH
        while z <= ztop + 1e-3:
            c = (a+b)/2 + n*.05; B.box('03_TOWER', 'tower_mullion', (c.x, c.y, z), (L, .1, .07), yaw=yaw); z += PH
others = lambda me: [o for o in ALL if o is not me]
curtain(TOWER, HGT['tower_parapetTop_m'], others(TOWER))
curtain(TOWER_FW, HGT['tower_front_west_roof_m'] + .4, others(TOWER_FW))   # M027: corner top at 40.33 (+ coping), fitted point
curtain(STEP_A, HGT['tower_step_roofs_m'][0], others(STEP_A), zbot=WALL_TOP)
curtain(STEP_B, HGT['tower_step_roofs_m'][1], others(STEP_B), zbot=WALL_TOP)
curtain(GBOX, M['glass_box']['top_m'], others(GBOX), zbot=WALL_TOP)
for poly, h in ((GBOX, M['glass_box']['top_m']), (TOWER, HGT['tower_roof_m']), (TOWER_FW, HGT['tower_front_west_roof_m']), (STEP_A, HGT['tower_step_roofs_m'][0]), (STEP_B, HGT['tower_step_roofs_m'][1])):
    cap('03_TOWER', 'roof', poly, h)
# north and north-east low parts: same white cladding, no shopfront detail (not seen in the 2025 photos)
for poly, h in ((ANNEX, HGT['north_annex_roof_m']), (NE, 35.99), (NE2, 34.41)):
    for a, b, L, t, n in edges(poly):
        if exterior(a, b, n, others(poly)): clad_white('01_WEST_WING', a, b, n, L, 0, h, RIB)
    cap('01_WEST_WING', 'roof', poly, h)
# tower roof: antennas, dish poles, plant (M002/M027)
for p, h in (((40.0, 13.5), 7.0), ((44.0, 14.0), 5.0), ((47.5, 30.0), 4.0), ((48.5, 45.0), 4.5)):
    B.cyl('06_ROOFTOP', 'steel', (p[0], p[1], HGT['tower_roof_m']), (p[0], p[1], HGT['tower_roof_m'] + h), .09)
    for k in range(3): B.box('06_ROOFTOP', 'steel', (p[0] + .3*math.cos(k*2.1), p[1] + .3*math.sin(k*2.1), HGT['tower_roof_m'] + h - .8), (.18, .18, 1.2))
for p in ((42.0, 20.0), (47.5, 38.0), (48.5, 52.0)):
    B.box('06_ROOFTOP', 'plant', (p[0], p[1], HGT['tower_roof_m'] + .9), (2.4, 3.2, 1.8))

# ---------------------------------------------------------------- 04 sign box on the south face (frame only; faces are era layer)
SB = M['sign_box']
sbc = Vector(((SB['x0']+SB['x1'])/2, (SB['front_y']+SB['back_y'])/2, (SB['z0']+SB['z1'])/2))
B.box('04_SIGN_BOX', 'box_grey', sbc, (SB['x1']-SB['x0'], SB['back_y']-SB['front_y'], SB['z1']-SB['z0']))
SBF = SB['front_y'] - .01     # the front plane signs mount on (faces -Y)

# ---------------------------------------------------------------- 05 podium at the corner (under the drum, 0 - 10.44 m)
corner = [V2(p) for p in ((25.7, 19.4), (27.1, 17.8), (33.6, 11.3), (35.0, 11.2), (35.0, 15.0), (28.2, 20.6))]   # inside the PLATEAU ground ring
corner = ccw(corner)
for a, b, L, t, n in edges(corner):
    wall('05_PODIUM', 'shop_glass', a, b, 0, 4.4, n, -.4); wall('05_PODIUM', 'interior', a, b, 0, 4.4, n, -2.5)
    wall('05_PODIUM', 'white_panel', a, b, 4.4, HGT['podium_corner_roof_m'], n)
cap('05_PODIUM', 'roof', corner, HGT['podium_corner_roof_m']); cap('05_PODIUM', 'soffit', corner, 4.4, down=True)
# south shopfront under the sign box, between the corner and the Eiraku building (STARBUCKS-era 'COFFEE' bay, M027)
for x0, x1 in ((35.0, 45.6),):
    a, b = Vector((x0, 11.1)), Vector((x1, 10.2)); n = Vector((0, -1))
    wall('05_PODIUM', 'shop_glass', a, b, 0, 4.4, n, -.3); wall('05_PODIUM', 'interior', a, b, 0, 4.4, n, -3)
    wall('05_PODIUM', 'box_grey', a, b, 4.4, SB['z0'], n)

# ---------------------------------------------------------------- 07 Eiraku building (separate building, own collection)
EH = HGT['eiraku_roof_m']
for a, b, L, t, n in edges(EIRAKU):
    if not exterior(a, b, n, [TOWER, TOWER_FW]): continue
    wall('07_EIRAKU', 'eiraku_wall', a, b, 4.2, EH, n)
    k = max(1, int(L // 1.6)); z = 6.0
    while z < EH - 3:
        for i in range(k):
            c = a + (b-a)*((i+.5)/k); p0, p1 = c - t*.55, c + t*.55
            wall('07_EIRAKU', 'ribbon_glass', p0, p1, z, z + 1.7, n, .02)
        z += 3.6
    wall('07_EIRAKU', 'shop_glass', a, b, 0, 4.2, n, -.3); wall('07_EIRAKU', 'interior', a, b, 0, 4.2, n, -2.5)
cap('07_EIRAKU', 'roof', EIRAKU, EH)

# ---------------------------------------------------------------- 08 era layer: signs, ads, screens
def sign_plane(coll, m, c, t, n, w, h, proud=.0):
    c = c + n*proud; a = c - t*w/2; b = c + t*w/2; z0, z1 = c.z - h/2, c.z + h/2
    B.quad(coll, m, [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)], uv=[(0, 0), (1, 0), (1, 1), (0, 1)])

def text_obj(body, size, coll, m, loc, yaw, font, extrude=.04, align='CENTER'):
    cu = bpy.data.curves.new(body, 'FONT'); cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = 'CENTER'
    cu.font = bpy.data.fonts.load(font, check_existing=True); o = bpy.data.objects.new(body, cu); matlib.collection(coll).objects.link(o)
    o.location = loc; o.rotation_euler = (math.pi/2, 0, yaw); o.data.materials.append(MAT[m]); return o

def fit_text(o, w, h):
    bpy.context.view_layer.update(); dx, dz = o.dimensions.x, o.dimensions.y
    s = min(w/max(dx, 1e-3), h/max(dz, 1e-3)); o.scale = (s, s, 1)

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FONT_JP = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
if ERA != 'none':
    SG = json.load(open(D(f'signage_{ERA}.json'))); CS = f'08_SIGNS_{ERA}'
    led_s = 3.0 if NIGHT else 2.2
    for s in SG['signs']:
        sid = s['id']; kind = s['kind']
        if s['on'] == 'sign_box_front':
            t = Vector((1, 0, 0)); n = Vector((0, -1, 0)); cx = sum(s['x'])/2; cz = sum(s['z'])/2
            w = s['x'][1]-s['x'][0]; h = s['z'][1]-s['z'][0]; c = Vector((cx, SBF, cz))
            if kind == 'letters':
                mat(sid, principled(sid, s['colour'], rough=.35, emit=s['colour'], estr=6 if NIGHT else 0))
                mat(sid+'_sub', principled(sid+'_sub', s['edge'], rough=.4, emit=s['edge'], estr=3 if NIGHT else 0))
                o = text_obj(s['text'], 1, CS, sid, (cx, SBF - .12, cz + h*.12), 0, FONT_B, extrude=.12); fit_text(o, w, h*.72)
                o2 = text_obj(s['sub'], 1, CS, sid+'_sub', (cx + w*.18, SBF - .05, s['z'][0] + h*.08), 0, FONT_B, extrude=.02); fit_text(o2, w*.45, h*.18)
            elif kind == 'image':
                mat(sid, textured(sid, os.path.join(TEX, s['image']), emit=s['emit_night'] if NIGHT else 0, alpha=True))
                sign_plane(CS, sid, c, t, n, w, h, .03)
            elif kind == 'led':
                mat(sid, emissive_image(sid, os.path.join(TEX, s['image']), s['strength_night'] if NIGHT else s['strength_day'], sat=1 if NIGHT else .8))
                sign_plane(CS, sid, c, t, n, w, h, .02)
        elif s['on'] == 'drum':
            mat(sid, textured(sid, os.path.join(TEX, s['image']), rough=.5, emit=s['emit_night'] if NIGHT else 0))
            a0, a1 = s['arc_deg']; z0, z1 = s['z']
            for i in range(NS):   # wrap on a ring 6 cm proud of the drum, UV 0-1 across the arc
                u0 = a0 + (a1-a0)*i/NS; u1 = a0 + (a1-a0)*(i+1)/NS; r = DRUM_R + .06
                p0 = DRUM_C + Vector((math.cos(math.radians(u0)), math.sin(math.radians(u0))))*r
                p1 = DRUM_C + Vector((math.cos(math.radians(u1)), math.sin(math.radians(u1))))*r
                # outward-facing ring 6 cm proud; u grows with the angle, which reads left-to-right from outside
                B.quad(CS, sid, [(p1.x, p1.y, z0), (p0.x, p0.y, z0), (p0.x, p0.y, z1), (p1.x, p1.y, z1)],
                       uv=[((i+1)/NS, 0), (i/NS, 0), (i/NS, 1), ((i+1)/NS, 1)])
        elif s['on'] == 'west_face':
            u0, u1 = s['u']; z0, z1 = s['z']; t3 = WEST_T.to_3d(); n3 = WEST_N.to_3d()
            # the west face runs south -> north from WEST_A; u is measured from its south end
            sa = WEST_A if WEST_A.y < WEST_B.y else WEST_B; tt = (WEST_B - WEST_A).normalized() * (1 if WEST_A.y < WEST_B.y else -1)
            c = (sa + tt*((u0+u1)/2)).to_3d() + Vector((0, 0, (z0+z1)/2)); t3 = tt.to_3d()
            if kind == 'printed':
                mat(sid, textured(sid, os.path.join(TEX, s['image']), emit=s['emit_night'] if NIGHT else 0))
                sign_plane(CS, sid, c, -t3 if WEST_N.dot(Vector((-1, 0))) > 0 else t3, n3, u1-u0, z1-z0, s['proud'])
                for zz in (z0 - .2, z1 + .2):   # banner frame
                    q = c + n3*s['proud']; B.beam(CS, 'steel_dark', (q - t3*(u1-u0)/2 + Vector((0, 0, zz - c.z))), (q + t3*(u1-u0)/2 + Vector((0, 0, zz - c.z))), .12)
            elif kind == 'letters':
                mat(sid, principled(sid, s['colour'], rough=.35, emit=s['colour'], estr=8 if NIGHT else 0))
                yaw = math.atan2(-n3.x, n3.y) + math.pi
                o = text_obj(s['text'], 1, CS, sid, c + n3*.35, math.atan2(n3.x, -n3.y), FONT_B, extrude=.15); fit_text(o, u1-u0, (z1-z0)*.75)
        elif s['on'] == 'corner':
            # blue-framed screen on the corner podium, facing the crossing (south-west)
            nrm = Vector((-.707, -.707, 0)); tt = Vector((.707, -.707, 0)); c = Vector((30.0, 12.0, sum(s['z'])/2)) + nrm*.6
            w = s['w']; h = s['z'][1]-s['z'][0]
            mat(sid+'_frame', principled(sid+'_frame', s['frame'], rough=.4, emit=s['frame'], estr=2 if NIGHT else 0))
            B.box(CS, sid+'_frame', c - nrm*.25, (w + .6, .5, h + 1.4), yaw=math.atan2(tt.y, tt.x))
            mat(sid, emissive_image(sid, os.path.join(TEX, s['image']), led_s, sat=1 if NIGHT else .8))
            sign_plane(CS, sid, c + Vector((0, 0, -.15)), tt, nrm, w, h, .02)
            mat(sid+'_label', principled(sid+'_label', (1, 1, 1), emit=(1, 1, 1), estr=4 if NIGHT else .5))
            o = text_obj(s['label'], 1, CS, sid+'_label', c + nrm*.05 + Vector((0, 0, h/2 + .35)), math.atan2(tt.y, tt.x), FONT_B, extrude=.01); fit_text(o, w*.35, .5)
        elif s['on'] == 'corner_west':
            nrm = Vector((-.707, -.707, 0)); tt = Vector((.707, -.707, 0)); c = Vector((27.4, 16.0, sum(s['z'])/2)) + nrm*.9
            h = s['z'][1]-s['z'][0]
            mat(sid, principled(sid, s['colour'], rough=.4, emit=s['colour'], estr=3 if NIGHT else 0))
            mat(sid+'_t', principled(sid+'_t', s['text_colour'], rough=.4, emit=s['text_colour'], estr=5 if NIGHT else 0))
            B.box(CS, sid, c, (s['w'], .35, h), yaw=math.atan2(tt.y, tt.x))
            for k, ch in enumerate(s['pre'] + s['text']):
                o = text_obj(ch, 1, CS, sid+'_t', c + nrm*.19 + Vector((0, 0, h/2 - .6 - k*h/6.6)), math.atan2(tt.y, tt.x), FONT_JP, extrude=.01)
                fit_text(o, s['w']*.62, h/7.5)
        elif s['on'] == 'eiraku_south':
            a, b = EIRAKU[0], EIRAKU[1]
            for p in EIRAKU:   # the south edge: the two lowest-y corners
                pass
            S_ = sorted(EIRAKU, key=lambda v: v.y)[:2]; a, b = sorted(S_, key=lambda v: v.x)
            t3 = (b-a).normalized().to_3d(); n3 = Vector((t3.y, -t3.x, 0)); w = (b-a).length + .4
            z0, z1 = s['z']; c = ((a+b)/2).to_3d() + Vector((0, 0, (z0+z1)/2)) + n3*.45
            mat(sid, principled(sid, s['colour'], rough=.4, emit=s['colour'], estr=2.5 if NIGHT else 0))
            mat(sid+'_t', principled(sid+'_t', s['text_colour'], rough=.4, emit=s['text_colour'], estr=4 if NIGHT else 0))
            B.box(CS, sid, c, (w, .3, z1 - z0 - .15), yaw=math.atan2(t3.y, t3.x))
            for k, ch in enumerate(s['text']):
                o = text_obj(ch, 1, CS, sid+'_t', c + n3*.16 + Vector((0, 0, (z1-z0)/2 - (k+.6)*(z1-z0)/(len(s['text'])+.2))), math.atan2(t3.y, t3.x), FONT_JP, extrude=.01)
                fit_text(o, w*.75, (z1-z0)/(len(s['text'])+.6))
    if any(s['on'] == 'eiraku_south' for s in SG['signs']):   # the sign frame on the Eiraku roof (signTop 38.6)
        S_ = sorted(EIRAKU, key=lambda v: v.y)[:2]
        for p in S_: B.beam(CS, 'steel_dark', (p.x, p.y + .4, EH), (p.x, p.y + .4, HGT['eiraku_signTop_m']), .15)

# ---------------------------------------------------------------- 09 context: pavement, roads (for the photo comparison only)
B.box('09_CONTEXT', 'pavement', (34, 38, -.08), (40, 70, .16))
B.box('09_CONTEXT', 'asphalt', (10, 0, -.12), (600, 600, .16))
B.finish()

# ================================================================ world, camera, render (as QFRONT v5)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; prev = QUALITY == 'preview'
sc.cycles.samples = 48 if prev else 192; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.transparent_max_bounces = 16; sc.cycles.glossy_bounces = 4
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.world = bpy.data.worlds.new('sky'); sc.world.use_nodes = True; nt = sc.world.node_tree
sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; bg = nt.nodes['Background']; nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
if NIGHT:
    nt.links.remove(bg.inputs['Color'].links[0]); bg.inputs['Color'].default_value = (.004, .006, .02, 1); bg.inputs['Strength'].default_value = 1.0
    sc.view_settings.exposure = 0.0
    for p, e in (((10, 0, 9), 6e3), ((20, -12, 9), 4e3), ((0, 25, 9), 4e3)):   # street light spill from the crossing
        ld = bpy.data.lights.new('street', 'AREA'); ld.energy = e; ld.size = 14; ld.color = (1, .85, .7)
        lo = bpy.data.objects.new('street', ld); sc.collection.objects.link(lo); lo.location = p
        lo.rotation_euler = (Vector((32, 25, 12)) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
else:
    # M027: 2025-09-01 13:18 JST -> sun azimuth ~207 deg, elevation ~57 deg (computed for 35.66 N, 139.70 E)
    az, el = math.radians(207), math.radians(57)
    sky.sun_elevation = el; sky.sun_rotation = math.radians(90 - 207 + 180); bg.inputs['Strength'].default_value = .22; sc.view_settings.exposure = 0.0
    sky.air_density = .8; sky.dust_density = .3; sky.ozone_density = 3.0; sky.sun_disc = False
    lp_ = nt.nodes.new('ShaderNodeLightPath'); deep = nt.nodes.new('ShaderNodeMix'); deep.data_type = 'RGBA'; deep.blend_type = 'MULTIPLY'
    deep.inputs[7].default_value = (.2, .33, .62, 1)
    nt.links.new(lp_.outputs['Is Camera Ray'], deep.inputs['Factor']); nt.links.new(sky.outputs['Color'], deep.inputs[6]); nt.links.new(deep.outputs[2], bg.inputs['Color'])
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 6.0; sun.color = (1.0, .96, .9); sun.angle = math.radians(.6)
    so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
    dirv = Vector((math.sin(az)*math.cos(el), math.cos(az)*math.cos(el), math.sin(el))); so.rotation_euler = (-dirv).to_track_quat('-Z', 'Y').to_euler()
HDRI = os.path.join(ROOT, '..', '..', 'qfront', 'source', 'hdri', 'shanghai_bund.hdr' if NIGHT else 'wide_street_01.hdr')
if os.path.exists(HDRI) and 'nohdri' not in argv:   # glossy rays mirror a built-up street (CC0 Poly Haven, shared with QFRONT)
    env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI)
    bg2 = nt.nodes.new('ShaderNodeBackground'); bg2.inputs['Strength'].default_value = .03 if NIGHT else .5
    hsv_ = nt.nodes.new('ShaderNodeHueSaturation'); hsv_.inputs['Saturation'].default_value = .6
    nt.links.new(env.outputs['Color'], hsv_.inputs['Color']); nt.links.new(hsv_.outputs['Color'], bg2.inputs['Color'])
    lpg = nt.nodes.new('ShaderNodeLightPath'); mxs = nt.nodes.new('ShaderNodeMixShader'); wout = nt.nodes['World Output']
    nt.links.new(lpg.outputs['Is Glossy Ray'], mxs.inputs['Fac']); nt.links.new(bg.outputs['Background'], mxs.inputs[1]); nt.links.new(bg2.outputs['Background'], mxs.inputs[2])
    nt.links.new(mxs.outputs['Shader'], wout.inputs['Surface'])

def camera_fit(name, fit, scale):
    """Pinhole camera from tools/camfit.py: compass yaw, pitch, roll, focal in px, principal point at the centre."""
    F = json.load(open(D(fit))); cam = bpy.data.cameras.new(name); co = bpy.data.objects.new(name, cam); sc.collection.objects.link(co)
    y, p, r = map(math.radians, (F['yaw'], F['pitch'], F['roll']))
    f = Vector((math.sin(y)*math.cos(p), math.cos(y)*math.cos(p), math.sin(p))); rt = Vector((math.cos(y), -math.sin(y), 0)); up = rt.cross(f)
    rt2 = rt*math.cos(r) - up*math.sin(r); up2 = up*math.cos(r) + rt*math.sin(r)
    co.matrix_world = Matrix((rt2, up2, -f)).transposed().to_4x4() @ Matrix.Identity(4); co.location = F['pos']
    sc.render.resolution_x, sc.render.resolution_y = int(F['W']*scale), int(F['H']*scale)
    cam.sensor_fit = 'HORIZONTAL'; cam.angle_x = 2*math.atan(F['W']/2/F['fpx']); cam.clip_end = 3000; sc.camera = co; return co, F

def camera_look(name, pos, target, lens, res):
    cam = bpy.data.cameras.new(name); co = bpy.data.objects.new(name, cam); sc.collection.objects.link(co)
    co.location = pos; co.rotation_euler = (Vector(target)-Vector(pos)).to_track_quat('-Z', 'Y').to_euler(); cam.lens = lens; cam.clip_end = 3000
    sc.render.resolution_x, sc.render.resolution_y = res; sc.camera = co

scale = .5 if prev else 1.0
if VIEW == 'm027': camera_fit('cam_m027', 'camera_m027_fit.json', scale)
elif VIEW == 'sw': camera_look('cam_sw', (-30, -35, 45), (38, 32, 18), 32, (int(1600*scale), int(1100*scale)))
elif VIEW == 'south': camera_look('cam_s', (40, -55, 4), (40, 15, 22), 30, (int(1100*scale), int(1400*scale)))
elif VIEW == 'roof': camera_look('cam_roof', (0, -10, 75), (38, 35, 30), 30, (int(1600*scale), int(1100*scale)))
elif VIEW == 'west': camera_look('cam_w', (-20, 42, 3), (30, 40, 18), 24, (int(1600*scale), int(1100*scale)))

_bd = opt('border', None)
if _bd and VIEW == 'm027':   # crop of the M027 frame in photo pixels (1280 x 1707); zoom=N renders it at N x
    x0, y0, x1, y1 = map(float, _bd.split(',')); F = json.load(open(D('camera_m027_fit.json')))
    sc.render.resolution_x, sc.render.resolution_y = F['W'], F['H']; sc.render.resolution_percentage = int(100*float(opt('zoom', '2')))
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x = x0/F['W'], x1/F['W']; sc.render.border_min_y, sc.render.border_max_y = 1 - y1/F['H'], 1 - y0/F['H']
    VIEW = 'm027crop_' + opt('tag', 'crop')
if 'clay' in argv:   # geometry check: neutral grey, glass kept
    clay = principled('clay', (.6, .6, .6), rough=.6)
    for ob in sc.objects:
        if ob.type in ('MESH', 'FONT') and not any(k in (ob.data.materials[0].name if ob.data.materials else '') for k in ('glass',)):
            ob.data.materials.clear(); ob.data.materials.append(clay)
    QUALITY += '_clay'
os.makedirs(OUT, exist_ok=True)
if ERA != '2025': QUALITY += f'_era-{ERA}'
sc.render.filepath = os.path.join(OUT, f'{MODE}_{VIEW}_{QUALITY}.png')
if 'save' in argv:   # fonts and sign textures packed; the HDRI stays a relative link to the QFRONT copy
    for f_ in bpy.data.fonts:
        if f_.filepath and f_.filepath != '<builtin>' and not f_.packed_file: f_.pack()
    for im in bpy.data.images:
        if im.filepath and TEX in bpy.path.abspath(im.filepath) and not im.packed_file: im.pack()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f'magnet_{MODE}.blend'), relative_remap=True)
if 'norender' not in argv: bpy.ops.render.render(write_still=True)
tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in sc.objects if o.type == 'MESH')
print(f'RENDERED {MODE} {VIEW} {QUALITY} tris={tris} objects={len(sc.objects)}')
