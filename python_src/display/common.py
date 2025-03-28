""" Common functions for displaying """
from typing import List

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def plot_line_collection(*args: List[LineCollection]):
    """ Plot a each line collection given as an argument """
    _, ax = plt.subplots(1)
    for arg in args:
        ax.add_collection(arg)

    ax.autoscale()
    ax.set_aspect('equal')

    plt.show()
