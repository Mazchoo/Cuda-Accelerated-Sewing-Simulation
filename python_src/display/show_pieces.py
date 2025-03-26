""" Show all pieces in 2D to inspect shape and turn-points """
import json

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
import matplotlib.cm as cm

from python_src.utils.geometry import points_along_contour

from python_src.parameters import NR_SEWING_POINTS


def get_hsv_colors(n):
    return [cm.hsv(i / n) for i in range(n)]


def show_each_piece(clothing_data: dict, offset: tuple):
    current_offset = np.array([0, 0], dtype=np.float64)
    all_contours = {}
    all_turn_points = {}

    for key, piece in clothing_data['pieces'].items():
        contour = np.array(piece["contour"], dtype=np.float64)
        contour += current_offset
        all_contours[key] = contour

        xs, ys = contour[:, 0], contour[:, 1]
        plt.plot(xs, ys, c='k', alpha=0.8)

        cog = np.array(piece["cog"], dtype=np.float64)
        cog += current_offset
        plt.text(*cog, key, c='r')

        turn_points = np.array(piece["turn_points"])
        turn_points += current_offset
        all_turn_points[key] = turn_points

        current_offset += offset

    colors = get_hsv_colors(len(clothing_data["sewing"]))

    # ToDo refactor to sewing and from sewing line into separate objects
    for i, sewing_pair in enumerate(clothing_data["sewing"]):
        from_contour = all_contours[sewing_pair['from_piece']]
        from_tp_start = all_turn_points[sewing_pair['from_piece']][sewing_pair['from_tp_index_1']]
        from_tp_end = all_turn_points[sewing_pair['from_piece']][sewing_pair['from_tp_index_2']]
        from_marker_start = sewing_pair['from_marker_start']
        from_marker_end = sewing_pair['from_marker_end']

        from_poly_exterior = Polygon(from_contour).exterior
        from_sewing_pts = points_along_contour(from_poly_exterior, from_tp_start, from_tp_end,
                                               from_marker_start, from_marker_end, NR_SEWING_POINTS)

        xs, ys = zip(*[[p.x, p.y] for p in from_sewing_pts])
        plt.plot(xs, ys, c=colors[i], linestyle='--', lw=2)

        plt.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]),
                     arrowprops=dict(arrowstyle='->', color=colors[i], lw=2))

        to_contour = all_contours[sewing_pair['to_piece']]
        to_tp_start = all_turn_points[sewing_pair['to_piece']][sewing_pair['to_tp_index_1']]
        to_tp_end = all_turn_points[sewing_pair['to_piece']][sewing_pair['to_tp_index_2']]
        to_marker_start = sewing_pair['to_marker_start']
        to_marker_end = sewing_pair['to_marker_end']

        to_poly_exterior = Polygon(to_contour).exterior
        to_sewing_pts = points_along_contour(to_poly_exterior, to_tp_start, to_tp_end,
                                             to_marker_start, to_marker_end, NR_SEWING_POINTS)

        xs, ys = zip(*[[p.x, p.y] for p in to_sewing_pts])
        plt.plot(xs, ys, c=colors[i], linestyle='--', lw=2)

        plt.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]),
                     arrowprops=dict(arrowstyle='->', color=colors[i], lw=2))

    plt.axis('equal')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    with open('./assets/sewing_shirt.json', 'r', encoding='utf-8') as f:
        clothing_data = json.load(f)
    show_each_piece(clothing_data, (100, 0))
