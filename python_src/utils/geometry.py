''' Helper geometry functions '''
import numpy as np
from shapely.geometry import LineString, Point


def points_along_contour(contour: LineString, start: list, end: list,
                         start_fraction: float, end_fraction: float, nr_points: int):
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
