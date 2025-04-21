""" Dispatch to annotate a mesh from different sources """
import numpy as np

from python_src.utils.geometry import get_point_on_contour
from shapely.geometry import Polygon

from python_src.parameters import CM_PER_M


def get_point_location(point_data, contour, all_turn_points):
    tp_start = all_turn_points[point_data['tp_begin']]
    tp_end = all_turn_points[point_data['tp_end']]
    snap_marker = point_data['marker']
    return get_point_on_contour(contour, tp_start,
                                tp_end, snap_marker)


def get_annotation_dict_from_piece_data(piece_data: dict) -> dict:
    """ Add annotations from piece """
    contour = Polygon(piece_data["contour"]).exterior
    turn_points = np.array(piece_data["turn_points"], dtype=np.float64)

    output = {}

    snap_point = get_point_location(piece_data["body_points"]["snap"], contour, turn_points)
    output[piece_data["body_points"]["snap"]["name"]] = np.array(
        [snap_point.x, snap_point.y, 0], dtype=np.float64
    ) / CM_PER_M

    alignment_point = get_point_location(piece_data["body_points"]["snap"], contour, turn_points)
    output[piece_data["body_points"]["alignment"]["name"]] = np.array(
        [alignment_point.x, alignment_point.y, 0], dtype=np.float64
    ) / CM_PER_M

    return output


def get_annotated_locations_from_dict(annotated_locations: dict) -> dict:
    """ Get annotation dict from annotated locations on body """
    return {name: np.array(point, dtype=np.float64) for name, point in annotated_locations.items()}
