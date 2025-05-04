""" Bend piece over mesh by using the normals of the mesh """
from typing import Optional

import numpy as np

from src.simulation.piece_physics import DynamicPiece
from src.simulation.mesh import MeshData
from src.utils.geometry import (get_closest_normal_on_mesh, get_each_point_distance_to_3d_line,
                                get_closest_line_origin_for_each_point, get_projections_onto_line_origins,
                                RotationPlaneData, get_bend_round_line_adjustment)

from src.parameters import WRAP_RADIANS


def get_perpedicular_alignment_along_piece(body_mesh: MeshData, piece: DynamicPiece,
                                           align_vector: np.ndarray) -> Optional[np.ndarray]:
    """ Get vector perpendicular to alignment and normal on body at snap-point """
    _, normal_at_snap = get_closest_normal_on_mesh(body_mesh.trimesh, piece.snap_point)
    vector_along_piece = np.cross(normal_at_snap, align_vector)
    vector_along_distance = np.linalg.norm(vector_along_piece)

    if vector_along_distance == 0:
        print(f'Normal at {piece.snap_point_name} is parallel to normal at body')
        return None

    vector_along_piece /= vector_along_distance
    return vector_along_piece


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
    bend_points = vertices_3d[~on_line_mask]

    vector_along_piece = get_perpedicular_alignment_along_piece(body_mesh, piece, align_vector)
    if vector_along_piece is None:
        return

    bend_point_to_line_index = get_closest_line_origin_for_each_point(bend_points, line_points, vector_along_piece)
    bend_line_origins = line_points[bend_point_to_line_index]
    projections = get_projections_onto_line_origins(bend_points, bend_line_origins, vector_along_piece)
    projections_sort_inds = np.argsort(projections)

    projections_sorted = projections[projections_sort_inds]
    positive_proj_inds = np.where(projections_sorted > 0)[0]
    postive_ind = len(projections) if len(positive_proj_inds) == 0 else positive_proj_inds[0]
    bend_inds = np.where(~on_line_mask)[0]
    bend_to_line_inds_sorted = bend_point_to_line_index[projections_sort_inds]

    # indices of points perpendicular to alignment on positve side of alignment line
    # sorted by their projection (or distance) from the alignment line
    postive_sorted_query_inds = bend_inds[projections_sort_inds][postive_ind:]
    negative_sorted_query_inds = bend_inds[projections_sort_inds][:postive_ind]

    for i, origin_point in enumerate(line_points):
        query_points_mask = bend_to_line_inds_sorted[postive_ind:] == i
        query_inds_to_adjust = postive_sorted_query_inds[query_points_mask]

        rotate_calculate_data = RotationPlaneData(np.cos(-WRAP_RADIANS), np.sin(-WRAP_RADIANS),
                                                  origin_point, align_vector)
        running_total_adjustment = np.zeros(3, dtype=np.float64)
        last_point = origin_point
        for query_ind in query_inds_to_adjust:
            vertices_3d[query_ind] += running_total_adjustment
            adjustment = get_bend_round_line_adjustment(
                vertices_3d[query_ind], last_point, rotate_calculate_data
            )
            vertices_3d[query_ind] += adjustment
            running_total_adjustment += adjustment
            last_point = vertices_3d[query_ind]

        query_points_mask = bend_to_line_inds_sorted[:postive_ind] == i
        query_inds_to_adjust = negative_sorted_query_inds[query_points_mask]

        rotate_calculate_data = RotationPlaneData(np.cos(WRAP_RADIANS), np.sin(WRAP_RADIANS),
                                                  origin_point, align_vector)
        running_total_adjustment = np.zeros(3, dtype=np.float64)
        last_point = origin_point
        for query_ind in query_inds_to_adjust[::-1]:
            vertices_3d[query_ind] += running_total_adjustment
            adjustment = get_bend_round_line_adjustment(
                vertices_3d[query_ind], last_point, rotate_calculate_data
            )
            vertices_3d[query_ind] += adjustment
            running_total_adjustment += adjustment
            last_point = vertices_3d[query_ind]
