""" Functions that deal with aligning a mesh to target points on another mesh """
import numpy as np

from src.simulation.piece_physics import DynamicPiece
from src.simulation.mesh import MeshData
from src.utils.geometry import get_alignment_matrix

from src.parameters import DISTANCE_FROM_BODY


def snap_and_align_piece_to_body(piece: DynamicPiece, body_mesh: MeshData):
    """ Snap piece so that piece point matches body plus some buffer zone """
    snap_point_name = piece.snap_point_name
    piece_snap_point = piece.snap_point
    body_snap_point = body_mesh.get_annotation(snap_point_name)

    if body_snap_point is None:
        print(f"Body does not contain snap-point {snap_point_name}")

    body_trimesh = body_mesh.trimesh
    (closest_point,), _, (triangle_id,) = body_trimesh.nearest.on_surface([body_snap_point])
    normal_to_surface = body_trimesh.face_normals[triangle_id]
    offset_target = closest_point + DISTANCE_FROM_BODY * normal_to_surface

    offset = offset_target - piece_snap_point
    piece.mesh.offset_vertices(offset)

    align_point_name = piece.alignment_point_name
    piece_align_point = piece.alignment_point
    body_align_point = body_mesh.get_annotation(align_point_name)

    if body_align_point is None:
        print(f"Body does not contain align-point {align_point_name}")

    (closest_point,), _, (triangle_id,) = body_trimesh.nearest.on_surface([body_align_point])
    normal_to_surface = body_trimesh.face_normals[triangle_id]
    align_target = closest_point + DISTANCE_FROM_BODY * normal_to_surface
    body_align_vector = align_target - offset_target

    piece_align_vector = piece_align_point - piece_snap_point
    piece_normal = np.array([0, 0, 1], dtype=np.float64)

    rotation_matrix = get_alignment_matrix(piece_align_vector, piece_normal, body_align_vector, normal_to_surface)
    piece.mesh.matrix_multiply(rotation_matrix, offset_target)
