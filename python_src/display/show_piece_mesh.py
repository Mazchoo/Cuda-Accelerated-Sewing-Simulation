""" Show the mesh of a piece in matplotlib """
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices


def convert_mesh_to_line_collection(vertex_data, index_data) -> LineCollection:
    """ Create matplotlib line collection from a mesh """
    lines = []

    for face in index_data:
        lines.append([vertex_data[face[0]][:2], vertex_data[face[1]][:2]])
        lines.append([vertex_data[face[1]][:2], vertex_data[face[2]][:2]])
        lines.append([vertex_data[face[2]][:2], vertex_data[face[0]][:2]])

    return LineCollection(lines, colors='blue', linewidths=2)


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
    vertex_data = clothing_display_data["L-1"]["vertex_data"] / 100.
    index_data = clothing_display_data["L-1"]["index_data"]

    line_collection = convert_mesh_to_line_collection(vertex_data, index_data)
    plot_line_collection(line_collection)
