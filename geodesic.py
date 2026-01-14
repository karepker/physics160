# geodesic.py - Geodesic Sphere Generation
#
# Original code: Copyright (c) 2003-2024 Adrian Rossiter <adrian_r@teleline.es>
# From the Antiprism project: https://github.com/antiprism/antiprism_python
# Licensed under MIT License - https://opensource.org/licenses/MIT
#
# Adapted for this project by Kar Epker (2012, 2026)
# Modifications: Python 3 compatibility, numpy array output, removed unused shapes

import collections
import math
from numpy import array, append


# Vector functions

def _vec_add(v0, v1):
    """v0 + v1"""
    return (v0[0] + v1[0], v0[1] + v1[1], v0[2] + v1[2])


def _vec_subtract(v0, v1):
    """v0 - v1"""
    return (v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2])


def _vec_scale(v0, s):
    """s * v0"""
    return (s * v0[0], s * v0[1], s * v0[2])


def _vec_len(v0):
    """length of v0"""
    return math.sqrt(v0[0] * v0[0] + v0[1] * v0[1] + v0[2] * v0[2])


def _np_to_array(np_arr):
    """Convert numpy 2D array [n, 3] to list of tuples [(x1, y1, z1), ...]."""
    return [(np_arr[i, 0], np_arr[i, 1], np_arr[i, 2]) for i in range(np_arr.shape[0])]


# Icosahedron generation

def _get_icosahedron():
    """Return vertices and faces for a unit icosahedron."""
    X = 0.525731112119133606
    Z = 0.850650808352039932

    verts = [
        (-X, 0.0, Z), (X, 0.0, Z), (-X, 0.0, -Z), (X, 0.0, -Z),
        (0.0, Z, X), (0.0, Z, -X), (0.0, -Z, X), (0.0, -Z, -X),
        (Z, X, 0.0), (-Z, X, 0.0), (Z, -X, 0.0), (-Z, -X, 0.0)
    ]

    faces = [
        (0, 4, 1), (0, 9, 4), (9, 5, 4), (4, 5, 8), (4, 8, 1),
        (8, 10, 1), (8, 3, 10), (5, 3, 8), (5, 2, 3), (2, 7, 3),
        (7, 10, 3), (7, 6, 10), (7, 11, 6), (11, 0, 6), (0, 1, 6),
        (6, 1, 10), (9, 0, 11), (9, 11, 2), (9, 2, 5), (7, 2, 11)
    ]

    return verts, faces


# Grid and point generation

def _sphere_projection(points):
    """Project points onto unit sphere (modifies in place)."""
    for i in range(len(points)):
        points[i] = _vec_scale(points[i], 1.0 / _vec_len(points[i]))


def _grid_to_points(grid, freq, f_verts, face):
    """Convert grid coordinates to 3D points on triangular face."""
    f_verts = _np_to_array(f_verts)
    points = []
    v = []

    for vtx in range(3):
        v.append([(0.0, 0.0, 0.0)])
        edge_vec = _vec_subtract(f_verts[(vtx + 1) % 3], f_verts[vtx])
        ang = 2 * math.asin(_vec_len(edge_vec) / 2.0)
        unit_edge_vec = _vec_scale(edge_vec, 1.0 / _vec_len(edge_vec))
        for i in range(1, freq + 1):
            length = math.sin(i * ang / freq) / math.sin(math.pi / 2 + ang / 2 - i * ang / freq)
            v[vtx].append(_vec_scale(unit_edge_vec, length))

    for (i, j) in grid.values():
        # Skip vertices
        if (i == 0) + (j == 0) + (i + j == freq) == 2:
            continue

        # Skip edges in one direction to avoid duplicates
        if (i == 0 and face[2] > face[0]) or (j == 0 and face[0] > face[1]) or (i + j == freq and face[1] > face[2]):
            continue

        n = [i, j, freq - i - j]
        v_delta = _vec_add(v[0][n[0]], _vec_subtract(v[-1 % 3][freq - n[1 % 3]], v[-1 % 3][freq]))
        pt = _vec_add(f_verts[0], v_delta)

        for k in [1, 2]:
            v_delta = _vec_add(v[k][n[k]], _vec_subtract(v[(k - 1) % 3][freq - n[(k + 1) % 3]], v[(k - 1) % 3][freq]))
            pt = _vec_add(pt, _vec_add(f_verts[k], v_delta))
        pt = _vec_scale(pt, 1.0 / 3)

        points.append(pt)

    return points


def _make_grid(freq, m, n):
    """Create geodesic subdivision pattern grid."""
    grid = collections.OrderedDict()
    for i in range(int(2 * freq / (m + n))):
        for j in range(int(2 * freq / (m + n))):
            x = i * (-n) + j * (m + n)
            y = i * (m + n) + j * (-m)

            if x >= 0 and y >= 0 and x + y <= freq:
                grid[(i, j)] = (x, y)

    return grid


# Public API

def make_sphere(shape, frequency, m, n):
    """
    Generate points on a geodesic sphere.

    Args:
        shape: Base polyhedron type ("i" for icosahedron)
        frequency: Subdivision frequency
        m, n: Class pattern parameters (1,0 for Class I)

    Returns:
        numpy array of shape [num_points, 3] with points on unit sphere
    """
    if shape != "i":
        raise ValueError(f"Only icosahedron shape ('i') is supported, got '{shape}'")

    verts, faces = _get_icosahedron()
    verts = array(verts)

    grid = _make_grid(frequency * (m ** 2 + m * n + n ** 2), 1, 0)
    points = array(verts)

    for face in faces:
        new_points = _grid_to_points(
            grid, frequency, array([verts[face[i]] for i in range(3)]), face
        )
        if new_points:
            points = append(points, array(new_points), axis=0)

    _sphere_projection(points)

    return points
