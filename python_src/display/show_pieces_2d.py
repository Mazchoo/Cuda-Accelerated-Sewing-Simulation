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


def show_sewing_line(sewing_line, all_contours, all_turn_points, color):
    contour = all_contours[sewing_line['piece']]
    tp_start = all_turn_points[sewing_line['piece']][sewing_line['tp_index_start']]
    tp_end = all_turn_points[sewing_line['piece']][sewing_line['tp_index_end']]
    marker_start = sewing_line['marker_start']
    marker_end = sewing_line['marker_end']

    from_poly_exterior = Polygon(contour).exterior
    from_sewing_pts = points_along_contour(from_poly_exterior, tp_start, tp_end,
                                           marker_start, marker_end, NR_SEWING_POINTS)

    xs, ys = zip(*[[p.x, p.y] for p in from_sewing_pts])
    plt.plot(xs, ys, c=color, linestyle='--', lw=2)

    plt.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]),
                 arrowprops=dict(arrowstyle='->', color=color, lw=2))


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
    for i, sewing_pair in enumerate(clothing_data["sewing"]):
        color = colors[i]
        show_sewing_line(sewing_pair["from"], all_contours, all_turn_points, color)
        show_sewing_line(sewing_pair["to"], all_contours, all_turn_points, color)

    plt.axis('equal')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    with open('./assets/sewing_shirt.json', 'r', encoding='utf-8') as f:
        clothing_data = json.load(f)
    show_each_piece(clothing_data, (100, 0))
