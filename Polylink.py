from math import sqrt, cos, sin, pi
from mathutils import Vector, Quaternion
from functools import reduce


class PolyMesh:
    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces

    def merge(self, another):
        new_vertices = self.vertices + another.vertices
        vSize = len(self.vertices)
        new_faces = self.faces + [[vSize + i for i in row]
                                  for row in another.faces]
        return PolyMesh(new_vertices, new_faces)


regularPolyhedra = {}

regularPolyhedra["TETRAHEDRON"] = PolyMesh(
    [Vector(i) for i in [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]],
    [[0, 3, 1], [0, 2, 3], [1, 3, 2], [0, 1, 2]])

regularPolyhedra["CUBE"] = PolyMesh(
    [Vector((i, j, k)) for i in [1, -1] for j in [1, -1] for k in [1, -1]],
    [[0, 2, 3, 1], [2, 6, 7, 3], [4, 5, 7, 6],
     [0, 1, 5, 4], [0, 4, 6, 2], [1, 3, 7, 5]])

regularPolyhedra["OCTAHEDRON"] = PolyMesh(
    [Vector(i) for i in
     [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]],
    [[0, 3, 5], [0, 5, 2], [2, 5, 1], [1, 5, 3],
     [0, 4, 3], [0, 2, 4], [1, 4, 2], [1, 3, 4]])

regularPolyhedra["DODECAHEDRON"] = PolyMesh(
    [Vector(k) for row in
     [[(0, i, j), (j, 0, i), (i, j, 0)]
      for i in [(sqrt(5)-1)/2, -(sqrt(5)-1)/2]
      for j in [(sqrt(5)+1)/2, -(sqrt(5)+1)/2]] for k in row] +
    [Vector((i, j, k)) for i in [1, -1] for j in [1, -1] for k in [1, -1]],
    [[0, 6, 14, 1, 12], [6, 0, 16, 4, 18], [6, 18, 11, 5, 14],
     [0, 12, 2, 8, 16], [4, 16, 8, 17, 10], [12, 1, 7, 13, 2],
     [18, 4, 10, 19, 11], [1, 14, 5, 15, 7], [2, 13, 3, 17, 8],
     [5, 11, 19, 9, 15], [3, 9, 19, 10, 17], [3, 13, 7, 15, 9]])

regularPolyhedra["ICOSAHEDRON"] = PolyMesh(
    [Vector(k) for row in [[(0, i, j), (j, 0, i), (i, j, 0)]
                           for i in [(sqrt(5)+1)/2, -(sqrt(5)+1)/2]
                           for j in [1, -1]] for k in row],
    [[0, 1, 2], [0, 2, 3], [0, 3, 8], [0, 8, 4], [0, 4, 1],
     [1, 4, 6], [1, 6, 5], [1, 5, 2], [2, 5, 7], [2, 7, 3],
     [3, 7, 10], [3, 10, 8], [8, 10, 11], [8, 11, 4], [4, 11, 6],
     [9, 5, 6], [9, 6, 11], [9, 11, 10], [9, 10, 7], [9, 7, 5]])


def vector_mean(vectors, num: int):
    return sum(vectors, Vector((0, 0, 0)))/num


def rotate_direction(rot: float, point: Vector,
                     center: Vector, normal: Vector):
    return (Quaternion(normal, rot) * point - center).normalized()


def getPolylinkInfo(polyName: str, rot: float, faceDis: float):
    vertices = regularPolyhedra[polyName].vertices
    faces = regularPolyhedra[polyName].faces
    faceVCoords = [[vertices[i] for i in face] for face in faces]
    frq = len(faceVCoords[0])
    faceCenters = [vector_mean(i, frq) for i in faceVCoords]
    faceNormals = [i.normalized() for i in faceCenters]
    xNs = [rotate_direction(rot, *i) for i in
           zip([x[0] for x in faceVCoords], faceCenters, faceNormals)]
    faceCenters = [faceDis * i for i in faceNormals]
    return (frq, faceCenters, faceNormals, xNs)


def trigCircleC(center: Vector, zN: Vector, xN: Vector,
                r: float, frq: int, atd: float):
    yN = zN.cross(xN)
    return lambda t: (center + (r + atd * cos(frq * t)) *
                      (cos(t) * xN + sin(t) * yN))


def trigCircleD1(zN: Vector, xN: Vector, r: float, frq: int, atd: float):
    yN = zN.cross(xN)
    return lambda t: ((r + atd * cos(frq * t)) * (yN * cos(t) - xN * sin(t)) -
                      atd * frq * (xN * cos(t) + yN * sin(t)) * sin(frq * t))


def trigCircleT(zN: Vector, xN: Vector, r: float, frq: int, atd: float):
    f = trigCircleD1(zN, xN, r, frq, atd)
    return lambda t: f(t).normalized()


def genTorusFaces(cSeg: int, lSeg: int):
    return [[j + cSeg * i, (j + cSeg * (i + 1)) % (cSeg * lSeg),
             (cSeg * (i + 1) + (j + 1) % cSeg) % (cSeg * lSeg),
             cSeg * i + (j + 1) % cSeg]
            for i in range(lSeg) for j in range(cSeg)]


def trigTorus(center: Vector, zN: Vector, xN: Vector,
              r: float, frq: int, atd: float,
              inradius: float, cSeg: int, lSeg: int):
    trigC = trigCircleC(center, zN, xN, r, frq, atd)
    trigT = trigCircleT(zN, xN, r, frq, atd)
    cPts = [2 * i * pi/cSeg for i in range(cSeg)]
    lPts = [2 * i * pi/lSeg for i in range(lSeg)]
    pts = [trigC(t) + inradius *
           (cos(ang) * zN + sin(ang) * zN.cross(trigT(t)))
           for t in lPts for ang in cPts]
    return PolyMesh(pts, genTorusFaces(cSeg, lSeg))


def trigPolylink(poly: str, rot: float, faceDis: float, r: float,
                 atd: float, inradius: float, fac: int, lSeg: int, cSeg: int):
    frq, faceCenters, faceNormals, xNs = getPolylinkInfo(poly, rot, faceDis)
    meshes = [trigTorus(*tup, r, fac * frq, atd, inradius, cSeg, lSeg)
              for tup in zip(faceCenters, faceNormals, xNs)]
    return reduce(lambda x, y: x.merge(y), meshes)
