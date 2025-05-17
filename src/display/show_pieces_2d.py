""" Show all pieces in 2D to inspect shape and turn-points """
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

from src.utils.geometry import points_along_contour
from src.utils.file_io import read_json
from src.display.common import get_hsv_colors
from src.simulation.mesh import get_point_location

NR_SEWING_POINTS = 10
FONT_SIZE = 16


def show_sewing_line(sewing_line, all_contours, all_turn_points, color):
    contour = all_contours[sewing_line['piece']]
    tp_start = all_turn_points[sewing_line['piece']][sewing_line['tp_index_start']]
    tp_end = all_turn_points[sewing_line['piece']][sewing_line['tp_index_end']]
    marker_start = sewing_line['marker_start']
    marker_end = sewing_line['marker_end']

    poly_exterior = Polygon(contour).exterior
    sewing_pts = points_along_contour(poly_exterior, tp_start, tp_end,
                                      marker_start, marker_end, NR_SEWING_POINTS)

    xs, ys = zip(*[[p.x, p.y] for p in sewing_pts])
    plt.plot(xs, ys, c=color, linestyle='--', lw=2)

    plt.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]),
                 arrowprops=dict(arrowstyle='->', color=color, lw=2))


def display_turnpoints(turn_points: np.ndarray):
    for i, (x, y) in enumerate(turn_points):
        plt.text(x, y, str(i))


def display_alignment(contour, body_points, all_turn_points):
    snap_point = get_point_location(body_points['snap'], contour, all_turn_points)
    alignment_point = get_point_location(body_points['alignment'], contour, all_turn_points)

    xs = [snap_point.x, alignment_point.x]
    ys = [snap_point.y, alignment_point.y]
    plt.plot(xs, ys, c='grey', linestyle=':', lw=2)
    plt.text(snap_point.x, snap_point.y, body_points['snap']['name'], fontsize=FONT_SIZE)
    plt.text(alignment_point.x, alignment_point.y, body_points['alignment']['name'], fontsize=FONT_SIZE)

    arrow_style = '-[' if body_points['alignment']['flip'] else '->'
    plt.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]),
                 arrowprops=dict(arrowstyle=arrow_style, color='grey', lw=2))


def show_pattern(clothing_data: dict, offset: tuple):
    current_offset = np.array([0, 0], dtype=np.float64)
    all_contours = {}
    all_turn_points = {}
    all_body_points = {}

    for key, piece in clothing_data['pieces'].items():
        contour = np.array(piece["contour"], dtype=np.float64)
        contour += current_offset
        all_contours[key] = contour

        xs, ys = contour[:, 0], contour[:, 1]
        plt.plot(xs, ys, c='k', alpha=0.8)

        cog = np.array(piece["cog"], dtype=np.float64)
        cog += current_offset
        plt.text(*cog, key, c='r', fontsize=FONT_SIZE)

        turn_points = np.array(piece["turn_points"], dtype=np.float64)
        turn_points += current_offset
        display_turnpoints(turn_points)

        all_turn_points[key] = turn_points
        all_body_points[key] = piece['body_points']

        current_offset += offset

    colors = get_hsv_colors(len(clothing_data["sewing"]))
    for i, sewing_pair in enumerate(clothing_data["sewing"]):
        color = colors[i]
        show_sewing_line(sewing_pair["from"], all_contours, all_turn_points, color)
        show_sewing_line(sewing_pair["to"], all_contours, all_turn_points, color)

    for key, contour_points in all_contours.items():
        contour = Polygon(contour_points).exterior
        body_points = all_body_points[key]
        turn_points = all_turn_points[key]
        display_alignment(contour, body_points, turn_points)

    plt.axis('equal')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    show_pattern(clothing_data, (100, 0))
