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


def length_along_contour(contour: LineString, start: list, end: list,
                         start_fraction: float, end_fraction: float) -> float:
    """
        Using a contour start and end find length along contour
    """
    marker_distance = contour.project(Point(end)) - contour.project(Point(start))
    fraction_difference = end_fraction - start_fraction

    return abs(marker_distance * fraction_difference)


def orthonormal_basis(v: np.ndarray, p: np.ndarray) -> np.ndarray:
    """
    Construct an orthonormal basis given a vector v and a perpendicular vector p.
    Returns a 3x3 matrix with columns [v̂, û, ŵ] where:
    - v̂ is the normalized v
    - û is the normalized component of p orthogonal to v
    - ŵ = v̂ x û
    """
    v_hat = v / np.linalg.norm(v)
    p_proj = p - np.dot(p, v_hat) * v_hat
    u_hat = p_proj / np.linalg.norm(p_proj)
    w_hat = np.cross(v_hat, u_hat)
    return np.stack([v_hat, u_hat, w_hat], axis=1)


def get_alignment_matrix(v1, p1, v2, p2):
    """
    Compute a unique rotation matrix that aligns:
    - v1 -> v2
    - p1 -> a perpendicular vector in the same relative orientation
    """
    B1 = orthonormal_basis(v1, p1)
    B2 = orthonormal_basis(v2, p2)

    R = B1 @ B2.T
    return R


if __name__ == '__main__':
    v1 = np.array([0, -1, 0], dtype=np.float64)
    p1 = np.array([1, 0, 0], dtype=np.float64)
    v2 = np.array([3/5, 0, 4/5], dtype=np.float64)
    p2 = np.array([-4/5, 0, 3/5], dtype=np.float64)
    R = get_alignment_matrix(v1, p1, v2, p2)
    v1 @= R
    p1 @= R
    print(v1, p1)
