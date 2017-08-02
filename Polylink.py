# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#
#  Contributor: Shengyi Wang
#  Contact:     txyyss@gmail.com
#

from math import sqrt, cos, sin, pi
from mathutils import Vector, Quaternion
from functools import reduce
from itertools import accumulate


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


def genTorusFaces(cSeg: int, lSeg: int):
    """Generate connecting ids for faces"""
    return [[j + cSeg * i, (j + cSeg * (i + 1)) % (cSeg * lSeg),
             (cSeg * (i + 1) + (j + 1) % cSeg) % (cSeg * lSeg),
             cSeg * i + (j + 1) % cSeg]
            for i in range(lSeg) for j in range(cSeg)]


# ********** Computation of Rotation Minimizing Frames ********** #


def computeRMF(x, t, r0: Vector):
    r = [r0]
    for i in range(len(t) - 1):
        v1 = x[i + 1] - x[i]
        c1 = v1.dot(v1)
        rL = r[i] - (2 / c1) * v1.dot(r[i]) * v1
        tL = t[i] - (2 / c1) * v1.dot(t[i]) * v1
        v2 = t[i + 1] - tL
        c2 = v2.dot(v2)
        r.append(rL - (2 / c2) * v2.dot(rL) * v2)
    return r


def euclideanDis(p1: Vector, p2: Vector):
    t = p1 - p2
    return sqrt(t.dot(t))


def accumulateLengths(x):
    return list(accumulate([euclideanDis(*i) for i in zip(x, x[1:])]))


def closedRMF(x, t, r0: Vector):
    xWrap = x + [x[0]]
    tWrap = t + [t[0]]
    r = computeRMF(xWrap, tWrap, r0)
    lengths = accumulateLengths(xWrap)
    totalLength = lengths[-1]
    lastR = r[-1]
    ang = (1 if t[0].dot(lastR.cross(r0)) > 0 else -1) * lastR.angle(r0)
    progress = [0] + [i * ang / totalLength for i in lengths]
    newR = [Quaternion(i[1], i[2]) * i[0] for i in zip(r, tWrap, progress)]
    return newR[:-1]


# ******************** Torus Polylink ******************** #


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


def trigTorus(center: Vector, zN: Vector, xN: Vector,
              r: float, frq: int, atd: float,
              inradius: float, initAng: float, cSeg: int, lSeg: int):
    """Generate a single wave-shaped torus"""
    trigC = trigCircleC(center, zN, xN, r, frq, atd)
    trigT = trigCircleT(zN, xN, r, frq, atd)
    cPts = [2 * i * pi/cSeg + initAng for i in range(cSeg)]
    lPts = [2 * i * pi/lSeg for i in range(lSeg)]
    pts = [trigC(t) + inradius *
           (cos(ang) * zN + sin(ang) * zN.cross(trigT(t)))
           for t in lPts for ang in cPts]
    return PolyMesh(pts, genTorusFaces(cSeg, lSeg))


def trigPolylink(poly: str, rot: float, faceDis: float, r: float,
                 atd: float, inradius: float, fac: int, iA: float,
                 lSeg: int, cSeg: int):
    """Generate torus-shaped regular polylink"""
    frq, faceCenters, faceNormals, xNs = getPolylinkInfo(poly, rot, faceDis)
    meshes = [trigTorus(*tup, r, fac * frq, atd, inradius, iA, cSeg, lSeg)
              for tup in zip(faceCenters, faceNormals, xNs)]
    return reduce(lambda x, y: x.merge(y), meshes)


# ******************** Torus Knot Polylink ******************** #


def torusKnotC(center: Vector, zN: Vector, xN: Vector,
               R: float, r: float, p: int, q: int):
    yN = zN.cross(xN)
    return lambda t: (center + (R + r * cos(q * t)) *
                      (xN * cos(p * t) + yN * sin(p * t)) +
                      r * zN * sin(q * t))


def torusKnotD1(zN: Vector, xN: Vector, R: float, r: float, p: int, q: int):
    yN = zN.cross(xN)
    return lambda t: (q * r * zN * cos(q * t) + p * (R + r * cos(q * t)) *
                      (yN * cos(p * t) - xN * sin(p * t)) -
                      q * r * (xN * cos(p * t) + yN * sin(p * t)) * sin(q * t))


def torusKnotT(zN: Vector, xN: Vector, R: float, r: float, p: int, q: int):
    f = torusKnotD1(zN, xN, R, r, p, q)
    return lambda t: f(t).normalized()


def torusKnot(center: Vector, zN: Vector, xN: Vector,
              R: float, r: float, p: int, q: int, inradius: float,
              initAng: float, cSeg: int, lSeg: int):
    tKC = torusKnotC(center, zN, xN, R, r, p, q)
    tKT = torusKnotT(zN, xN, R, r, p, q)
    cPts = [2 * i * pi/cSeg + initAng for i in range(cSeg)]
    lPts = [2 * i * pi/lSeg for i in range(lSeg)]
    spinePts = [tKC(i) for i in lPts]
    spineTs = [tKT(i) for i in lPts]
    r0 = (q * r * zN + p * (r+R) * zN.cross(xN)).cross(
        - ((p * p + q * q) * r + p * p * R) * xN)
    r0.normalize()
    spineRs = closedRMF(spinePts, spineTs, r0)
    pts = [i[0] + inradius * (cos(ang) * i[1].cross(i[2]) + sin(ang) * i[2])
           for i in zip(spinePts, spineTs, spineRs) for ang in cPts]
    return PolyMesh(pts, genTorusFaces(cSeg, lSeg))


def torusKnotPolylink(poly: str, rot: float, faceDis: float, R: float,
                      r: float, p: int, qFac: int, inradius: float,
                      initAng: float, cSeg: int, lSeg: int):
    frq, faceCenters, faceNormals, xNs = getPolylinkInfo(poly, rot, faceDis)
    meshes = [torusKnot(*tup, R, r, p, qFac * frq,
                        inradius, initAng, cSeg, lSeg)
              for tup in zip(faceCenters, faceNormals, xNs)]
    return reduce(lambda x, y: x.merge(y), meshes)
