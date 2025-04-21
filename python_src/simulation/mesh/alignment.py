""" Functions that deal with aligning a mesh to target points on another mesh """
from python_src.simulation.piece_physics import DynamicPiece
from python_src.simulation.mesh import MeshData

from python_src.parameters import DISTANCE_FROM_BODY


def snap_piece_to_body(piece: DynamicPiece, body_mesh: MeshData):
    """ Snap piece so that piece point matches body plus some buffer zone """
    snap_point_name = piece.snap_point_name
    piece_snap_point = piece.snap_point
    body_snap_point = body_mesh.get_annotation(snap_point_name)

    if body_snap_point is None:
        return KeyError(f"Body does not contain snap-point {snap_point_name}")

    body_trimesh = body_mesh.trimesh
    (closest_point,), _, (triangle_id,) = body_trimesh.nearest.on_surface([body_snap_point])
    normal_to_surface = body_trimesh.face_normals[triangle_id]
    offset_target = closest_point + DISTANCE_FROM_BODY * normal_to_surface

    offset = offset_target - piece_snap_point
    piece.mesh.offset_vertices(offset)
