""" Show the mesh of a piece in matplotlib """
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices


def plot_line_collection(line_collection: LineCollection):
    """ Plot a line collection """
    _, ax = plt.subplots(1)
    ax.add_collection(line_collection)

    ax.autoscale()
    ax.set_aspect('equal')

    plt.show()


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data = extract_all_piece_vertices(clothing_data)

    mesh = clothing_display_data["L-1"]
    line_collection = mesh.create_line_collection(colors='blue', linewidths=2)

    plot_line_collection(line_collection)
