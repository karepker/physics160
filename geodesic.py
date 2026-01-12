##################################################################
## GEODESIC SPHERE CREATION, by Adrian Rossiter, adapted by Kar Epker
##################################################################

import collections
import math
from numpy import array, append


# vector functions

# convert numpy 2D array of form [n, 3] to 1D array of form [(x1, y1, z1), ... , (xn, yn, zn)]
def np_to_array(np):
    to_return = []
    for i in range(np.shape[0]):
        entry = (np[i, 0], np[i, 1], np[i, 2])
        to_return.append(entry)
    return to_return


# v0 + v1
def vec_add(v0, v1):
    return (v0[0]+v1[0], v0[1]+v1[1], v0[2]+v1[2])


# v0 - v1
def vec_subtract(v0, v1):
    return (v0[0]-v1[0], v0[1]-v1[1], v0[2]-v1[2])


# s * v0
def vec_scale(v0, s):
    return (s*v0[0], s*v0[1], s*v0[2])


# length v0
def vec_len(v0):
    return math.sqrt(v0[0]*v0[0] + v0[1]*v0[1] + v0[2]*v0[2])


# cross product v0xv1
def vec_cross(v0, v1):
    return (v1[2]*v0[1] - v1[1]*v0[2], v1[0]*v0[2] - v1[2]*v0[0], v1[1]*v0[0] - v1[0]*v0[1])


# scalar product v0.v1
def vec_scalar(v0, v1):
    return v0[0]*v1[0] + v0[1]*v1[1] + v0[2]*v1[2]


# individual shape functions

def get_octahedron(verts, faces):
    X = 0.25*math.sqrt(2)
    verts.extend([(0.0, 0.5, 0.0), (X, 0.0, -X), (X, 0.0, X), (-X, 0.0, X),
                  (-X, 0.0, -X), (0.0, -0.5, 0.0)])

    faces.extend([(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),
                  (5, 2, 1), (2, 5, 3), (3, 5, 4), (4, 5, 1)])


def get_tetrahedron(verts, faces):
    X = 1/math.sqrt(3)
    verts.extend([(-X, X, -X), (-X, -X, X), (X, X, X), (X, -X, -X)])
    faces.extend([(0, 1, 2), (0, 3, 1), (0, 2, 3), (2, 1, 3)])


def get_triangle(verts, faces):
    if 1:
        Y = math.sqrt(3.0)/12.0
        Z = -0.8
        verts.extend([(-0.25, -Y, Z), (0.25, -Y, Z), (0.0, 2*Y, Z)])
        faces.extend([(0, 1, 2)])
    else:
        X = .525731112119133606
        Z = .850650808352039932
        verts.extend([(-X, 0.0, -Z), (X, 0.0, -Z), (0.0, Z, -X), (0.0, -Z, -X)])
        faces.extend([(0, 1, 2), (0, 3, 1)])


def get_icosahedron(verts, faces):
    X = .525731112119133606
    Z = .850650808352039932

    verts.extend([(-X, 0.0, Z), (X, 0.0, Z), (-X, 0.0, -Z), (X, 0.0, -Z),
                  (0.0, Z, X), (0.0, Z, -X), (0.0, -Z, X), (0.0, -Z, -X),
                  (Z, X, 0.0), (-Z, X, 0.0), (Z, -X, 0.0), (-Z, -X, 0.0)])

    faces.extend([(0, 4, 1), (0, 9, 4), (9, 5, 4), (4, 5, 8), (4, 8, 1),
                  (8, 10, 1), (8, 3, 10), (5, 3, 8), (5, 2, 3), (2, 7, 3),
                  (7, 10, 3), (7, 6, 10), (7, 11, 6), (11, 0, 6), (0, 1, 6),
                  (6, 1, 10), (9, 0, 11), (9, 11, 2), (9, 2, 5), (7, 2, 11)])


# determine which polygon to create

def get_poly(poly, verts, edges, faces):
    if poly == "i":
        get_icosahedron(verts, faces)
    elif poly == "o":
        get_octahedron(verts, faces)
    elif poly == "t":
        get_tetrahedron(verts, faces)
    elif poly == "T":
        get_triangle(verts, faces)
    else:
        return 0

    for face in faces:
        for i in range(0, len(face)):
            i2 = i+1
            if(i2 == len(face)):
                i2 = 0

        if face[i] < face[i2]:
            edges[(face[i], face[i2])] = 0
        else:
            edges[(face[i2], face[i])] = 0

    return 1


# create and arrange points

def sphere_projection(points):
    for i in range(len(points)):
        points[i] = vec_scale(points[i], 1.0/vec_len(points[i]))


def grid_to_points(grid, freq, div_by_len, f_verts, face):
    f_verts = np_to_array(f_verts)
    points = []
    v = []
    for vtx in range(3):
        v.append([(0.0, 0.0, 0.0)])
        edge_vec = vec_subtract(f_verts[(vtx+1) % 3], f_verts[vtx])
        if div_by_len:
            for i in range(1, freq+1):
                v[vtx].append(vec_scale(edge_vec, float(i)/freq))
        else:
            ang = 2*math.asin(vec_len(edge_vec)/2.0)
            unit_edge_vec = vec_scale(edge_vec, 1.0/vec_len(edge_vec))
            for i in range(1, freq+1):
                length = math.sin(i*ang/freq)/math.sin(math.pi/2 + ang/2 - i*ang/freq)
                v[vtx].append(vec_scale(unit_edge_vec, length))

    for (i, j) in grid.values():
        # skip vertex
        if (i == 0) + (j == 0) + (i+j == freq) == 2:
            continue

        # skip edges in one direction
        if (i == 0 and face[2] > face[0]) or (j == 0 and face[0] > face[1]) or (i+j == freq and face[1] > face[2]):
            continue

        n = [i, j, freq - i - j]
        v_delta = vec_add(v[0][n[0]], vec_subtract(v[(0-1) % 3][freq-n[(0+1) % 3]], v[(0-1) % 3][freq]))
        pt = vec_add(f_verts[0], v_delta)
        if not div_by_len:
            for k in [1, 2]:
                v_delta = vec_add(v[k][n[k]], vec_subtract(v[(k-1) % 3][freq-n[(k+1) % 3]], v[(k-1) % 3][freq]))
                pt = vec_add(pt, vec_add(f_verts[k], v_delta))
            pt = vec_scale(pt, 1.0/3)
        points.append(pt)

    return points


def make_grid(freq, m, n):
    grid = collections.OrderedDict()  # changed this to use Ordered dict instead of dict
    for i in range(int(2*freq/(m+n))):  # changed this to cast result to an int
        for j in range(int(2*freq/(m+n))):
            x = i*(-n) + j*(m+n)
            y = i*(m+n) + j*(-m)

            if x >= 0 and y >= 0 and x+y <= freq:
                grid[(i, j)] = (x, y)

    return grid


def make_sphere(shape, frequency, m, n):
    verts = []
    edges = {}
    faces = []
    get_poly(shape, verts, edges, faces)
    verts = array(verts)

    grid = {}
    grid = make_grid(frequency * (m**2 + m * n + n**2), 1, 0)

    points = array(verts)

    for row in faces:
        if shape == "T":
            face_edges = (0, 0, 0)  # generate points for all edges
        else:
            face_edges = row

        new_points = grid_to_points(grid, frequency, 0, array([verts[row[i]] for i in range(3)]), face_edges)
        np_new_points = array(new_points)

        if not len(new_points) == 0:  # don't append if there are no new points
            points = append(points, np_new_points, axis=0)

    sphere_projection(points)

    return points
