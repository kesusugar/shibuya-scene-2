# QFRONT Photorealism Challenge - Phase 1 design blockout (structure diagram, not the final model).
#
#   blender -b -P blender/blockout.py -- <outdir>
#
# Builds every component of the planned model as simple colour-coded geometry, at the dimensions in
# docs/DESIGN.md, so the component plan can be checked against photographs before Phase 2 detailing.
# Units: metres. Blender Z up; X east; Y north. Footprint: OSM way/136691386 (curved front) checked
# against PLATEAU 2025 LOD2 (pentagon, roof steps 44.0 / 48.4 / 52.1 m).
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---- dimensions (DESIGN.md section 3) --------------------------------------------------------
H_PODIUM = 6.0          # 1F
H_2F = 11.4             # top of 2F (Starbucks, braced double-height zone up to 3F band)
STOREY = 5.4            # 3F..8F
H_TOP = 44.0            # top storey roof (PLATEAU)
H_DECK = 48.4           # recessed roof deck (PLATEAU)
H_CROWN = 52.1          # crown screen parapet (PLATEAU)
CAVITY = 0.9            # double-skin: outer fin screen to inner glass
FIN_PITCH = 1.0         # outer vertical fins (photo count, to be confirmed by camera solve)
FIN_DEPTH, FIN_W = 0.32, 0.07
SCREEN = (14.0, 38.0)   # Q's EYE band on the curved front (LED 453 m2 total, main 99.5 m2 - Sony 2013)

# scene coords (x east, z south) -> Blender (x, y=-z)
P = lambda x, z: (x, -z)

# ---- footprint: straight faces + fitted arc on the crossing front -----------------------------
def circle3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d
    uy = ((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d
    return (ux, uy), math.hypot(ax-ux, ay-uy)
front = [P(1.04, -31.3), P(-4.63, -29.96), P(-10.75, -28.98), P(-16.64, -29.73)]
(cx, cy), R = circle3(front[0], front[2], front[3])
a0 = math.atan2(front[0][1]-cy, front[0][0]-cx); a1 = math.atan2(front[3][1]-cy, front[3][0]-cx)
sweep = (a1 - a0 + math.pi) % (2*math.pi) - math.pi; a1 = a0 + sweep
arc = [(cx+R*math.cos(a0+(a1-a0)*i/24), cy+R*math.sin(a0+(a1-a0)*i/24)) for i in range(25)]
outline = [P(-24.84, -56.49), P(5.08, -47.97), P(4.44, -45.32)] + arc + [P(-30.19, -43.09)]
# make counter-clockwise
area = sum(outline[i][0]*outline[(i+1)%len(outline)][1]-outline[(i+1)%len(outline)][0]*outline[i][1] for i in range(len(outline)))
if area < 0: outline.reverse()
print(f'front arc radius {R:.1f} m, footprint area {abs(area)/2:.0f} m2')

def offset(poly, d):
    """Inward offset of a CCW polygon by d (miter)."""
    n = len(poly); out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i-1]), Vector(poly[i]), Vector(poly[(i+1) % n])
        e1 = (p1-p0).normalized(); e2 = (p2-p1).normalized()
        n1 = Vector((-e1.y, e1.x)); n2 = Vector((-e2.y, e2.x))
        bis = (n1+n2); bis = bis.normalized() if bis.length > 1e-6 else n1
        out.append(tuple(p1 + bis * d / max(.3, bis.dot(n1))))
    return out

MAT = {}
def mat(name, rgb):
    if name in MAT: return MAT[name]
    m = bpy.data.materials.new(name); m.diffuse_color = (*rgb, 1); m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*rgb, 1)
    MAT[name] = m; return m

def obj(name, bm, material, coll):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); coll.objects.link(o); me.materials.append(mat(*material)); return o

def coll(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); return c

def prism(bm, poly, z0, z1):
    vs0 = [bm.verts.new((x, y, z0)) for x, y in poly]; vs1 = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(vs0[::-1]); bm.faces.new(vs1)
    for i in range(len(poly)):
        j = (i+1) % len(poly); bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))

def box(bm, c, size, yaw):
    r = bmesh.ops.create_cube(bm, size=1)['verts']
    for v in r: v.co = Vector((v.co.x*size[0], v.co.y*size[1], v.co.z*size[2]))
    bmesh.ops.rotate(bm, verts=r, cent=(0, 0, 0), matrix=Matrix.Rotation(yaw, 3, 'Z'))
    bmesh.ops.translate(bm, verts=r, vec=Vector(c))

def along(poly, step, closed=True):
    """Points every `step` m along the polyline, with the outward normal (CCW polygon)."""
    pts = []; n = len(poly); carry = 0
    for i in range(n if closed else n-1):
        a, b = Vector(poly[i]), Vector(poly[(i+1) % n]); L = (b-a).length
        if L < 1e-6: continue
        t = (b-a)/L; nrm = Vector((t.y, -t.x)); s = carry
        while s < L: pts.append((a+t*s, nrm, t)); s += step
        carry = s-L
    return pts

inner = offset(outline, CAVITY)
C_STRUCT, C_GLASS, C_SKIN, C_SCREEN, C_CROWN, C_GROUND, C_FIX = (coll(n) for n in
    ('01_STRUCTURE', '02_INNER_GLASS', '03_OUTER_FIN_SKIN', '04_QS_EYE', '05_CROWN', '06_GROUND_FLOOR', '07_FIXTURES'))

# 01 structure: slabs + core
bm = bmesh.new()
levels = [0.0, H_PODIUM, H_2F] + [H_2F + STOREY*k for k in range(1, 7)]
for z in levels[1:]: prism(bm, offset(outline, CAVITY+.15), z-.35, z)
prism(bm, offset(outline, CAVITY+.15), H_TOP-.5, H_TOP)
obj('SLABS', bm, ('struct', (.55, .55, .58)), C_STRUCT)
bm = bmesh.new(); core = offset(outline, 9.0); prism(bm, core, 0, H_DECK)
obj('CORE', bm, ('core', (.35, .35, .38)), C_STRUCT)

# 02 inner glass envelope
bm = bmesh.new(); prism(bm, inner, H_PODIUM, H_TOP); obj('INNER_GLASS', bm, ('glass', (.25, .45, .62)), C_GLASS)
bm = bmesh.new(); prism(bm, offset(outline, CAVITY+1.6), 0, H_PODIUM); obj('PODIUM_GLASS', bm, ('shopglass', (.95, .75, .35)), C_GROUND)

# 03 outer skin: fins + transoms (screen band left open on the front so the LED reads)
bm = bmesh.new()
for p, nrm, t in along(outline, FIN_PITCH):
    yaw = math.atan2(t.y, t.x)
    box(bm, (p.x + nrm.x*.1, p.y + nrm.y*.1, (H_PODIUM+H_CROWN)/2), (FIN_W, FIN_DEPTH, H_CROWN-H_PODIUM), yaw)
obj('OUTER_FINS', bm, ('fin', (.9, .9, .92)), C_SKIN)
bm = bmesh.new()
for z in [H_PODIUM + 2.7*k for k in range(1, 15)]:
    for i in range(len(outline)):
        a, b = Vector(outline[i]), Vector(outline[(i+1) % len(outline)]); L = (b-a).length
        if L < .05: continue
        m = (a+b)/2; t = (b-a)/L; nrm = Vector((t.y, -t.x))
        box(bm, (m.x+nrm.x*.05, m.y+nrm.y*.05, z), (L+.02, .3, .12), math.atan2(t.y, t.x))
obj('TRANSOMS', bm, ('transom', (.75, .76, .8)), C_SKIN)

# 04 Q's EYE: LED surface on the arc, between inner glass and fins
bm = bmesh.new(); arc_in = [tuple(Vector(p) + (Vector((cx, cy))-Vector(p)).normalized()*.45) for p in arc]
for i in range(len(arc_in)-1):
    (x0, y0), (x1, y1) = arc_in[i], arc_in[i+1]
    vs = [bm.verts.new(v) for v in ((x0, y0, SCREEN[0]), (x1, y1, SCREEN[0]), (x1, y1, SCREEN[1]), (x0, y0, SCREEN[1]))]
    bm.faces.new(vs)
obj('QS_EYE_LED', bm, ('led', (.9, .1, .55)), C_SCREEN)

# 05 crown: fin screen continues (above), steel truss inside, recessed deck, plant, lettering
bm = bmesh.new(); prism(bm, offset(outline, 3.0), H_TOP, H_DECK); obj('ROOF_DECK', bm, ('deck', (.5, .45, .4)), C_CROWN)
bm = bmesh.new()
ring = offset(outline, 1.6)
for p, nrm, t in along(ring, 4.5):
    box(bm, (p.x, p.y, (H_TOP+H_CROWN)/2), (.35, .35, H_CROWN-H_TOP), 0)          # posts
for z in (H_TOP+2.6, H_DECK+1.2, H_CROWN-.4):
    for i in range(len(ring)):
        a, b = Vector(ring[i]), Vector(ring[(i+1) % len(ring)]); L = (b-a).length
        if L < .05: continue
        m = (a+b)/2; t = (b-a)/L; box(bm, (m.x, m.y, z), (L, .3, .3), math.atan2(t.y, t.x))
for p, nrm, t in along(ring, 4.5):                                                   # diagonals
    v = Vector((p.x, p.y, (H_TOP+H_CROWN)/2)); d = Vector((t.x*4.5, t.y*4.5, H_CROWN-H_TOP))
    r = bmesh.ops.create_cube(bm, size=1)['verts']
    for q in r: q.co = Vector((q.co.x*.22, q.co.y*.22, q.co.z*d.length))
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix()
    bmesh.ops.rotate(bm, verts=r, cent=(0, 0, 0), matrix=rot); bmesh.ops.translate(bm, verts=r, vec=v + Vector((t.x, t.y, 0))*2.25)
obj('CROWN_TRUSS', bm, ('steel', (.15, .15, .17)), C_CROWN)
bm = bmesh.new(); mid = arc[12]; nrm = (Vector(mid)-Vector((cx, cy))).normalized(); tang = Vector((-nrm.y, nrm.x))
box(bm, (mid[0]+nrm.x*.5, mid[1]+nrm.y*.5, H_CROWN-2.2), (14, .25, 2.6), math.atan2(tang.y, tang.x))
obj('QFRONT_LETTERS', bm, ('letters', (1, 1, 1)), C_CROWN)

# 06 ground floor: canopy over the crossing frontage, 2F-3F X braces (Starbucks / SHARE LOUNGE)
bm = bmesh.new()
for i in range(0, len(arc)-1, 1):
    (x0, y0), (x1, y1) = arc[i], arc[i+1]; m = ((x0+x1)/2, (y0+y1)/2); nrm = (Vector(m)-Vector((cx, cy))).normalized()
    box(bm, (m[0]+nrm.x*1.2, m[1]+nrm.y*1.2, H_PODIUM-.2), (math.hypot(x1-x0, y1-y0)+.05, 2.4, .35), math.atan2(y1-y0, x1-x0))
obj('CANOPY', bm, ('canopy', (.8, .8, .82)), C_GROUND)
bm = bmesh.new()
for k in range(4):
    i = 3 + k*6; (x0, y0), (x1, y1) = offset(arc, 0)[i], offset(arc, 0)[i+5] if i+5 < len(arc) else arc[-1]
    a = Vector(arc_in[i]) + (Vector((cx, cy))-Vector(arc_in[i])).normalized()*.6; b = Vector(arc_in[min(i+5, len(arc_in)-1)]) + (Vector((cx, cy))-Vector(arc_in[min(i+5, len(arc_in)-1)])).normalized()*.6
    for (p0, z0, p1, z1) in ((a, H_PODIUM, b, H_2F+STOREY), (b, H_PODIUM, a, H_2F+STOREY)):
        d = Vector((p1.x-p0.x, p1.y-p0.y, z1-z0)); r = bmesh.ops.create_cube(bm, size=1)['verts']
        for q in r: q.co = Vector((q.co.x*.5, q.co.y*.5, q.co.z*d.length))
        bmesh.ops.rotate(bm, verts=r, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix())
        bmesh.ops.translate(bm, verts=r, vec=Vector((p0.x, p0.y, z0)) + d/2)
obj('X_BRACES', bm, ('brace', (.85, .85, .88)), C_GROUND)

# 07 fixtures: floodlight arms on the two front corners, TSUTAYA vertical letters on the east face
bm = bmesh.new()
for corner in (arc[0], arc[-1]):
    for k in range(6):
        box(bm, (corner[0], corner[1], 37.0 + k*.9), (1.6, .25, .25), 0)
obj('FLOODLIGHTS', bm, ('flood', (1, .9, .3)), C_FIX)
bm = bmesh.new(); a, b = Vector(P(5.08, -47.97)), Vector(P(4.44, -45.32)); e = Vector(P(1.04, -31.3))
t = (e-b).normalized(); nrm = Vector((t.y, -t.x))
for k, ch in enumerate('TSUTAYA'):
    p = b + t*(2+k*1.9); box(bm, (p.x+nrm.x*.4, p.y+nrm.y*.4, 30-k*3.4), (.15, 2.4, 2.8), math.atan2(t.y, t.x))
obj('TSUTAYA_LETTERS', bm, ('tsutaya', (.1, .1, .1)), C_FIX)

# ground + context
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=90)
for v in bm.verts: v.co += Vector((-12, 42, -.02))
obj('GROUND', bm, ('ground', (.42, .42, .42)), sc.collection)

# ---- renders: workbench, object colour, outline ----------------------------------------------
# Cycles CPU (no GPU/EGL in this container): flat-ish studio light, Freestyle outlines for a drawing look.
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 16; sc.cycles.use_denoising = True
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True
bg = sc.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.85, .88, .93, 1); bg.inputs[1].default_value = 1.0
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 2.2; so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(150))
sc.render.use_freestyle = True; sc.render.line_thickness = .6
sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1100, 1400
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
def shoot(name, pos, tgt, lens=30, res=None, hide=()):
    for c in bpy.data.collections: c.hide_render = c.name in hide
    co.location = Vector(pos); co.rotation_euler = (Vector(tgt)-Vector(pos)).to_track_quat('-Z', 'Y').to_euler(); cam.lens = lens
    if res: sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True)
front_dir = (Vector(arc[12]) - Vector((cx, cy))).normalized()
eye = Vector(arc[12]) + front_dir*62
shoot('blockout_front', (eye.x, eye.y, 1.7), (arc[12][0], arc[12][1], 24), lens=20, res=(1100, 1400))
shoot('blockout_axo', (eye.x+30, eye.y-25, 70), (-12, 42, 24), lens=28, res=(1400, 1100))
shoot('blockout_skin_off', (eye.x+30, eye.y-25, 70), (-12, 42, 24), lens=28, res=(1400, 1100), hide=('03_OUTER_FIN_SKIN',))
shoot('blockout_plan', (-12, 42, 160), (-12, 42.001, 0), lens=55, res=(1100, 1100), hide=('05_CROWN',))
print('OK blockout', R)
