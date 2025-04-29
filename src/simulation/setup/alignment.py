""" Functions that deal with aligning a mesh to target points on another mesh """
from typing import Optional

import numpy as np

from src.simulation.piece_physics import DynamicPiece
from src.simulation.mesh import MeshData
from src.utils.geometry import get_alignment_matrix, get_closest_normal_on_mesh

from src.parameters import DISTANCE_FROM_BODY
Z_VECTOR = np.array([0, 0, 1], dtype=np.float64)  # Always normal to 2d piece


def offset_piece_to_snap_point(piece: DynamicPiece, body_mesh: MeshData) -> Optional[np.ndarray]:
    """ Move piece snap-point to body snap-point, return None if snap point undefined """
    snap_point_name = piece.snap_point_name
    piece_snap_point = piece.snap_point
    body_snap_point = body_mesh.get_annotation(snap_point_name)

    if body_snap_point is None:
        print(f"Body does not contain snap-point {snap_point_name}")
        return None

    offset_target, _ = get_closest_normal_on_mesh(body_mesh.trimesh, body_snap_point,
                                                  DISTANCE_FROM_BODY)

    offset = offset_target - piece_snap_point
    piece.mesh.offset_vertices(offset)

    return offset_target


def rotate_point_to_alignment(piece: DynamicPiece, body_mesh: MeshData,
                              snap_point: np.ndarray) -> Optional[np.ndarray]:
    """ Use alignment points to rotate alignment """
    align_point_name = piece.alignment_point_name
    piece_align_point = piece.alignment_point
    body_align_point = body_mesh.get_annotation(align_point_name)

    if body_align_point is None:
        print(f"Body does not contain align-point {align_point_name}")
        return None

    align_target, normal_to_surface = get_closest_normal_on_mesh(body_mesh.trimesh, body_align_point,
                                                                 DISTANCE_FROM_BODY)
    body_align_vector = align_target - snap_point
    if np.linalg.norm(body_align_vector) == 0.:
        print(f"Alignment vector has zero distance {align_point_name}")
        return None

    piece_align_vector = piece_align_point - snap_point
    if np.linalg.norm(piece_align_vector) == 0.:
        print(f"Piece vector has zero distance {align_point_name}")
        return None

    rotation_matrix = get_alignment_matrix(piece_align_vector, Z_VECTOR,
                                           body_align_vector, normal_to_surface)
    piece.mesh.matrix_multiply(rotation_matrix, snap_point)
    return rotation_matrix


def snap_and_align_piece_to_body(piece: DynamicPiece, body_mesh: MeshData):
    """ Snap piece so that piece point matches body plus some buffer zone """
    if (snap_point := offset_piece_to_snap_point(piece, body_mesh)) is None:
        return

    rotate_point_to_alignment(piece, body_mesh, snap_point)
