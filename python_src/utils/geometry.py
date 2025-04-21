''' Helper geometry functions '''
from typing import List

import numpy as np
from shapely.geometry import LineString, Point


def get_point_on_contour(contour: LineString, start: list, end: list, marker: float) -> Point:
    """ Get point defined by the fraction between two distinct points on the contour """
    start_marker = contour.project(Point(start))
    end_marker = contour.project(Point(end))

    if start_marker > end_marker and end_marker == 0.:  # Not ideal solution but we have looped around
        end_marker = contour.length

    interpolated_marker = start_marker + marker * (end_marker - start_marker)
    return contour.interpolate(interpolated_marker)


def points_along_contour(contour: LineString, start: list, end: list,
                         start_fraction: float, end_fraction: float, nr_points: int) -> List[Point]:
    """
        Using a contour start and end find evenly spaced points on the contour between them
        with a start fraction and end fraction between the start and end
    """
    output = []

    start_marker = contour.project(Point(start))
    end_marker = contour.project(Point(end))

    for fraction in np.linspace(start_fraction, end_fraction, nr_points):
        marker = start_marker + fraction * (end_marker - start_marker)
        output.append(contour.interpolate(marker))

    return output


def rotation_matrix_from_vectors(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """
    Returns the rotation matrix that aligns v1 to v2.

    Parameters
    ----------
    v1 : array_like, shape (3,)
        Source vector.
    v2 : array_like, shape (3,)
        Target vector.

    Returns
    -------
    R : ndarray, shape (3, 3)
        Rotation matrix satisfying R @ v1 ≈ v2.
    """
    # Normalize input vectors
    a = v1 / np.linalg.norm(v1)
    b = v2 / np.linalg.norm(v2)

    # Cross product and dot product
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)

    # If vectors are parallel (cross product ~ 0)
    if np.isclose(s, 0):
        if c > 0:
            # Same direction: identity rotation
            return np.eye(3)
        else:
            # Opposite direction: 180° rotation around any perpendicular axis
            # Find an arbitrary orthogonal axis
            axis = np.array([1, 0, 0])
            if np.allclose(a, axis):
                axis = np.array([0, 1, 0])
            v = np.cross(a, axis)
            v /= np.linalg.norm(v)
            K = np.array([
                [0, -v[2], v[1]],
                [v[2], 0, -v[0]],
                [-v[1], v[0], 0]
            ], dtype=np.float64)
            # Rodrigues for 180°: R = I + 2 K^2
            return np.eye(3) + 2 * (K @ K)

    # General case
    K = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ], dtype=np.float64)
    # Rodrigues' rotation formula
    R = np.eye(3) + K + (K @ K) * ((1 - c) / (s**2))
    return R
