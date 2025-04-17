""" Dispatch to annotate a mesh from different sources """
import numpy as np

from python_src.utils.geometry import get_point_on_contour
from python_src.simulation.mesh import MeshData
from shapely.geometry import Polygon


def get_point_location(point_data, contour, all_turn_points):
    tp_start = all_turn_points[point_data['tp_begin']]
    tp_end = all_turn_points[point_data['tp_end']]
    snap_marker = point_data['marker']
    return get_point_on_contour(contour, tp_start,
                                tp_end, snap_marker)


def annotate_mesh_from_piece_data(mesh: MeshData, piece: dict):
    """ Add annotations from piece """
    contour = Polygon(piece["contour"]).exterior
    turn_points = np.array(piece["turn_points"], dtype=np.float64)

    snap_point = get_point_location(piece["body_points"]["snap"], contour, turn_points)
    mesh.add_annotation(piece["body_points"]["snap"]["name"],
                        np.array([snap_point.x, snap_point.y, 0], dtype=np.float64))

    alignment_point = get_point_location(piece["body_points"]["snap"], contour, turn_points)
    mesh.add_annotation(piece["body_points"]["alignment"]["name"],
                        np.array([alignment_point.x, alignment_point.y, 0], dtype=np.float64))
