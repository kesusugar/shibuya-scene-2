"""Partition planar triangles at polygon edge lines, preserving their interpolated Z.

Every resulting convex piece lies on one side of every boundary line. Its
centroid therefore classifies it even when the mask polygon is concave.
No Blender dependency: the geometry routine is also exercised outside Blender.
"""
EPS = 1e-9


def contains(p, polygon):
    x, y = p[:2]
    inside = False
    for i, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
            inside = not inside
    return inside


def side(p, a, b):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def clip(piece, a, b, sign):
    result = []
    previous = piece[-1]
    dp = sign * side(previous, a, b)
    for current in piece:
        dc = sign * side(current, a, b)
        if (dp >= 0) != (dc >= 0):
            t = dp / (dp-dc)
            result.append(tuple(previous[k]+t*(current[k]-previous[k]) for k in range(3)))
        if dc >= 0:
            result.append(current)
        previous, dp = current, dc
    # A vertex exactly on the line can otherwise appear twice.
    clean = []
    for p in result:
        if not clean or sum((p[k]-clean[-1][k])**2 for k in range(3)) > EPS**2:
            clean.append(p)
    if len(clean)>1 and sum((clean[0][k]-clean[-1][k])**2 for k in range(3)) <= EPS**2:
        clean.pop()
    return clean


def partition(triangle, polygon):
    pieces = [triangle]
    for i, a in enumerate(polygon):
        b = polygon[i-1]
        next_pieces = []
        for piece in pieces:
            distances = [side(p,a,b) for p in piece]
            if min(distances)<-EPS and max(distances)>EPS:
                next_pieces.extend(p for p in (clip(piece,a,b,1),clip(piece,a,b,-1)) if len(p)>=3)
            else:
                next_pieces.append(piece)
        pieces = next_pieces
    return [(piece,contains(tuple(sum(p[k] for p in piece)/len(piece) for k in range(3)),polygon)) for piece in pieces]
