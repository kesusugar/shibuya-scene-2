# Back-project photo pixels onto a vertical facade plane with a fitted camera.
#   python3 backproject.py <fit.json> <plane: x0,y0,x1,y1> u,v [u,v ...]
import sys, json, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0]); from camfit import basis
C = json.load(open(sys.argv[1])); x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
a = np.array([x0, y0, 0.]); t = np.array([x1-x0, y1-y0, 0.]); L = np.linalg.norm(t); t /= L; n = np.array([-t[1], t[0], 0.])
f, rt, up = basis(C['yaw'], C['pitch'], C['roll']); o = np.array(C['pos'], float)
for s in sys.argv[3:]:
    u, v = map(float, s.split(','))
    d = f + rt*(u - C['W']/2)/C['fpx'] - up*(v - C['H']/2)/C['fpx']
    k = ((a - o) @ n)/(d @ n); p = o + k*d
    print(f"px {u:6.0f},{v:6.0f} -> along {((p-a)@t):6.2f} m of {L:.1f}, z {p[2]:6.2f} m, dist {k*np.linalg.norm(d):5.1f} m")
