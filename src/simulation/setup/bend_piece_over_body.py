""" Bend piece over mesh by using the normals of the mesh """
from typing import NamedTuple

import numpy as np

from src.simulation.piece_physics import DynamicPiece
from src.simulation.mesh import MeshData
from src.utils.geometry import (get_closest_normal_on_mesh, get_each_point_distance_to_3d_line,
                                get_closest_line_origin_for_each_point, get_projections_onto_line_origins)

from src.parameters import BEND_OVER_PIECE_RADIANS


class RotationPlaneData(NamedTuple):
    """ Pre-computed information to rotate a point in plane perpendicular to 3d line """
    cos_theta: np.float64
    sin_theta: np.float64
    line_origin: np.ndarray
    line_vector: np.ndarray


def bend_point_round_line(current_point: np.ndarray, prev_point: np.ndarray, total_adjustment: np.ndarray,
                          theta: float, line_origin: np.ndarray, line_vector: np.ndarray):
    """ Adjust point to rotate in plane perpendicular to line """
    current_point += total_adjustment

    vector = current_point - prev_point

    point_distance = np.linalg.norm(vector)
    if point_distance == 0.:
        print("Warning!: Two points on mesh appear at same location")
        return total_adjustment

    offset_point = current_point - line_origin
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    rotated_current_point = offset_point * cos_theta + sin_theta * np.cross(line_vector, offset_point)
    rotated_current_point += line_vector * np.dot(line_vector, offset_point) * (1 - cos_theta)
    target_point = line_origin + rotated_current_point

    target_point_vector = target_point - prev_point
    target_point_vector_norm = np.linalg.norm(target_point_vector)
    if target_point_vector_norm == 0.:
        # print("Warning!: Adusting point parallel to norm")
        return total_adjustment

    adjustment = target_point_vector / target_point_vector_norm * point_distance
    current_point += adjustment
    total_adjustment += adjustment

    return total_adjustment


def bend_piece_over_body(piece: DynamicPiece, body_mesh: MeshData, threshold: float) -> np.ndarray:
    """
        Use closest point on body and gravity to get a better initialisation for sleeve
        Generic way of doing this is to associate each point with a bone line
        and then rotate around the bone line
    """

    piece_snap_point = piece.snap_point
    align_vector = piece.align_vector

    align_distance = np.linalg.norm(align_vector)
    if align_distance == 0.:
        print(f"Alignment point is same location as snap point {piece.snap_point_name} -> {piece.alignment_point_name}")
        return
    align_vector /= align_distance

    vertices_3d = piece.mesh.vertices_3d
    on_line_mask = get_each_point_distance_to_3d_line(vertices_3d, align_vector, piece_snap_point) <= threshold

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

    query_point_to_line_index = get_closest_line_origin_for_each_point(query_points, line_points, vector_along_piece)
    query_line_origins = line_points[query_point_to_line_index]
    projections = get_projections_onto_line_origins(query_points, query_line_origins, vector_along_piece)
    projections_sort_inds = np.argsort(projections)

    projections_sorted = projections[projections_sort_inds]
    positive_proj_inds = np.where(projections_sorted > 0)[0]
    postive_ind = len(projections) if len(positive_proj_inds) == 0 else positive_proj_inds[0]
    query_inds = np.where(~on_line_mask)[0]
    query_to_line_inds_sorted = query_point_to_line_index[projections_sort_inds]

    # indices of points perpendicular to alignment on positve side of alignment line
    # sorted by their projection (or distance) from the alignment line
    postive_sorted_query_inds = query_inds[projections_sort_inds][postive_ind:]
    negative_sorted_query_inds = query_inds[projections_sort_inds][:postive_ind]

    for i, origin_point in enumerate(line_points):
        query_points_mask = query_to_line_inds_sorted[postive_ind:] == i
        query_inds_to_adjust = postive_sorted_query_inds[query_points_mask]

        running_total_adjustment = np.zeros(3, dtype=np.float64)
        last_point = origin_point
        for query_ind in query_inds_to_adjust:
            running_total_adjustment = bend_point_round_line(
                vertices_3d[query_ind], last_point, running_total_adjustment,
                -BEND_OVER_PIECE_RADIANS, origin_point, align_vector
            )
            last_point = vertices_3d[query_ind]

        query_points_mask = query_to_line_inds_sorted[:postive_ind] == i
        query_inds_to_adjust = negative_sorted_query_inds[query_points_mask]

        running_total_adjustment = np.zeros(3, dtype=np.float64)
        last_point = origin_point
        for query_ind in query_inds_to_adjust[::-1]:
            running_total_adjustment = bend_point_round_line(
                vertices_3d[query_ind], last_point, running_total_adjustment,
                BEND_OVER_PIECE_RADIANS, origin_point, align_vector
            )
            last_point = vertices_3d[query_ind]
