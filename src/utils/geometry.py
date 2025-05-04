''' Helper geometry functions '''
from typing import List, Tuple, NamedTuple

import numpy as np
from trimesh import Trimesh
from shapely.geometry import LineString, Point


class RotationPlaneData(NamedTuple):
    """ Pre-computed information to rotate a point in plane perpendicular to 3d line """
    cos_theta: np.float64
    sin_theta: np.float64
    line_origin: np.ndarray
    line_vector: np.ndarray


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


def get_closest_normal_on_mesh(trimesh: Trimesh, query_point: np.ndarray,
                               distance: float = 0.) -> Tuple[np.ndarray, np.ndarray]:
    """ Get offset by normal to closest point on trimesh """
    (closest_point,), _, (triangle_id,) = trimesh.nearest.on_surface([query_point])
    normal_to_surface = trimesh.face_normals[triangle_id]
    offset_point = closest_point + distance * normal_to_surface
    return offset_point, normal_to_surface


def get_each_point_distance_to_3d_line(points: np.ndarray, vector: np.ndarray,
                                       origin: np.ndarray) -> np.ndarray:
    """ Get distance for every point in points to a 3d line """
    offset_points = points - origin
    cross_prod = np.cross(offset_points, vector)
    return np.linalg.norm(cross_prod, axis=1)


def get_closest_line_origin_for_each_point(points: np.ndarray,
                                           line_origins: np.ndarray, line_vector: np.ndarray):
    """ Return the index of the closest line starting at origin for each query point """
    distances = np.array([
        get_each_point_distance_to_3d_line(points, line_vector, origin) for origin in line_origins
    ], dtype=np.float64)
    return np.argmin(distances, axis=0)


def get_projections_onto_line_origins(points: np.ndarray, line_origins: np.ndarray,
                                      line_vector: np.ndarray) -> np.ndarray:
    """ Get projection (distance postive or negative)
        along different lines with varying origins but the same vector
    """
    offset_points = points - line_origins
    return np.dot(offset_points, line_vector)


def rotate_point_in_3d_plane(point: np.ndarray, plane: RotationPlaneData):
    """ Rotate a point on plane perpendicular to 3d line using Rodrigues rotation formula """
    point_vector = point - plane.line_origin

    rotated_current_point = point_vector * plane.cos_theta
    rotated_current_point += plane.sin_theta * np.cross(plane.line_vector, point_vector)
    rotated_current_point += plane.line_vector * np.dot(plane.line_vector, point_vector) * (1 - plane.cos_theta)

    return plane.line_origin + rotated_current_point


def get_bend_round_line_adjustment(current_point: np.ndarray, prev_point: np.ndarray,
                                   rotate_plane_data: RotationPlaneData):
    """
        Return adjustment amount for point to rotate in plane perpendicular to line
        On failure, zero adjustment is returned
    """
    vector = current_point - prev_point

    point_distance = np.linalg.norm(vector)
    if point_distance == 0.:
        print("Warning!: Two points on mesh appear at same location")
        return np.zeros(3, dtype=np.float64)

    target_point = rotate_point_in_3d_plane(current_point, rotate_plane_data)
    target_point_vector = target_point - prev_point

    target_point_vector_norm = np.linalg.norm(target_point_vector)
    if target_point_vector_norm == 0.:
        print("Warning!: Adusting point parallel to norm")
        return np.zeros(3, dtype=np.float64)

    return target_point_vector / target_point_vector_norm * point_distance


if __name__ == '__main__':
    v1 = np.array([0, -1, 0], dtype=np.float64)
    p1 = np.array([1, 0, 0], dtype=np.float64)
    v2 = np.array([3/5, 0, 4/5], dtype=np.float64)
    p2 = np.array([-4/5, 0, 3/5], dtype=np.float64)
    R = get_alignment_matrix(v1, p1, v2, p2)
    v1 @= R
    p1 @= R
    print(v1, p1)
