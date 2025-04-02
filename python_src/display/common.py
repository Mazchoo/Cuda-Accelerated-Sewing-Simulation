""" Common functions for displaying """
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.cm as cm
import numpy as np


def plot_line_collection(*args: List[LineCollection]):
    """ Plot a each line collection given as an argument """
    _, ax = plt.subplots(1)
    for arg in args:
        ax.add_collection(arg)

    ax.autoscale()
    ax.set_aspect('equal')

    plt.show()


def get_hsv_colors(n) -> List[Tuple[np.float64, np.float64, np.float64]]:
    """ Get n colors in RGB format """
    return [cm.hsv(i / n) for i in range(n)]


def float_rgb_to_str(rgb: Tuple[np.float64, np.float64, np.float64]) -> float:
    """ Convert matplotlit float color to css style color """
    r, g, b = [int(255 * c) for c in rgb]
    return f'rgb({r}, {g}, {b})'
