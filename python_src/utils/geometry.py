''' Helper geometry functions '''
from typing import List

import numpy as np
from shapely.geometry import LineString, Point


def get_point_on_contour(contour: LineString, start: list, end: list, marker: float) -> Point:
    """ Get point defined by the fraction between two distinct points on the contour """
    start_marker = contour.project(Point(start))
    end_marker = contour.project(Point(end))

    if start_marker > end_marker and end_marker == 0.:  # Not ideal solution but we have looped around
        end_marker = contour.length

    interpolated_marker = start_marker + marker * (end_marker - start_marker)
    return contour.interpolate(interpolated_marker)


def points_along_contour(contour: LineString, start: list, end: list,
                         start_fraction: float, end_fraction: float, nr_points: int) -> List[Point]:
    """
        Using a contour start and end find evenly spaced points on the contour between them
        with a start fraction and end fraction between the start and end
    """
    output = []

    start_marker = contour.project(Point(start))
    end_marker = contour.project(Point(end))

    for fraction in np.linspace(start_fraction, end_fraction, nr_points):
        marker = start_marker + fraction * (end_marker - start_marker)
        output.append(contour.interpolate(marker))

    return output
