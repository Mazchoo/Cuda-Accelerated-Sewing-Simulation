""" Bend piece over mesh by using the normals of the mesh """
import numpy as np
from trimesh import Trimesh

from src.simulation.piece_physics import DynamicPiece
from src.simulation.mesh import MeshData
from src.utils.geometry import get_closest_normal_on_mesh


def get_distances_to_line(points: np.ndarray, vector: np.ndarray,
                          origin: np.ndarray) -> np.ndarray:
    """ Get distance for every point to a 3d line """
    offset_points = points - origin
    cross_prod = np.cross(offset_points, vector)
    return np.linalg.norm(cross_prod, axis=1)


def get_closest_line_for_each_point(line_origins: np.ndarray, line_vector: np.ndarray,
                                    query_points: np.ndarray):
    """ Return the index of the closest line starting at origin for each query point """
    distances = np.array([
        get_distances_to_line(query_points, line_vector, origin) for origin in line_origins
    ], dtype=np.float64)
    return np.argmin(distances, axis=0)


def get_query_point_projections(query_points: np.ndarray, query_line_origins: np.ndarray,
                                line_vector: np.ndarray) -> np.ndarray:
    """ Get projection amount on line """
    offset_points = query_points - query_line_origins
    return np.dot(offset_points, line_vector)


def bend_point_over_mesh(current_point: np.ndarray, prev_point: np.ndarray,
                         total_adjustment: np.ndarray, trimesh: Trimesh) -> np.ndarray:
    """
        Get adjustment to adjust point, assuming previous point has been adjusted by running total
        Returns new running total and adjusts current point in place
    """
    current_point += total_adjustment

    vector = current_point - prev_point

    point_distance = np.linalg.norm(vector)
    if point_distance == 0.:
        print("Warning!: Two points on mesh appear at same location")
        return total_adjustment

    _, normal_to_mesh = get_closest_normal_on_mesh(trimesh, current_point)
    parallel_vector = vector - np.dot(vector, normal_to_mesh) * normal_to_mesh

    parallel_norm = np.linalg.norm(parallel_vector)
    if parallel_norm == 0.:
        print("Warning!: Adusting point parallel to norm")
        return total_adjustment

    adjustment = parallel_vector / parallel_norm * point_distance
    current_point += adjustment
    total_adjustment += adjustment

    return total_adjustment


def bend_piece_over_body(piece: DynamicPiece, body_mesh: MeshData, threshold: float) -> np.ndarray:
    """ Use normal to body mesh at every point perpendicular to the alignment vector """
    piece_snap_point = piece.snap_point
    piece_align_point = piece.alignment_point
    align_vector = piece_align_point - piece_snap_point
    align_distance = np.linalg.norm(align_vector)

    if align_distance == 0.:
        print(f"Alignment point is same location as snap point {piece.snap_point_name} -> {piece.alignment_point_name}")
        return

    align_vector /= align_distance
    vertices_3d = piece.mesh.vertices_3d
    on_line_mask = get_distances_to_line(vertices_3d, align_vector, piece_snap_point) <= threshold

    if not np.any(on_line_mask):
        print(f"No points near alignment line {piece.snap_point_name} -> {piece.alignment_point_name}")
        return

    line_points = vertices_3d[on_line_mask]
    query_points = vertices_3d[~on_line_mask]
    _, normal_at_snap = get_closest_normal_on_mesh(body_mesh.trimesh, piece_snap_point)
    vector_along_piece = np.cross(normal_at_snap, align_vector)
    vector_along_distance = np.linalg.norm(vector_along_piece)

    if vector_along_distance == 0:
        print(f'Normal at {piece.snap_point_name} is parallel to normal at body')
        return

    vector_along_piece /= vector_along_distance

    query_point_to_line_index = get_closest_line_for_each_point(line_points, vector_along_piece, query_points)
    query_line_origins = line_points[query_point_to_line_index]
    projections = get_query_point_projections(query_points, query_line_origins, vector_along_piece)
    projections_sort_inds = np.argsort(projections)

    projections_sorted = projections[projections_sort_inds]
    positive_proj_inds = np.where(projections_sorted > 0)[0]
    postive_ind = len(projections) if len(positive_proj_inds) == 0 else positive_proj_inds[0]
    query_inds = np.where(~on_line_mask)[0]
    query_to_line_inds_sorted = query_point_to_line_index[projections_sort_inds]

    for i, origin_point in enumerate(line_points):
        query_points_mask = query_to_line_inds_sorted[postive_ind:] == i
        query_inds_to_adjust = query_inds[postive_ind:][query_points_mask]

        running_total_adjustment = np.zeros(3, dtype=np.float64)
        last_point = origin_point
        for query_ind in query_inds_to_adjust:
            running_total_adjustment = bend_point_over_mesh(
                vertices_3d[query_ind], last_point, running_total_adjustment, body_mesh.trimesh
            )
            last_point = vertices_3d[query_ind]
