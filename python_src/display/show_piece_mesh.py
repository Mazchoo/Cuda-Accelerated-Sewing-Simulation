""" Show the mesh of a piece in matplotlib """
from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices

from python_src.display.common import plot_line_collection


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data = extract_all_piece_vertices(clothing_data)

    mesh = clothing_display_data["L-1"].mesh
    line_collection = mesh.create_line_collection(colors='blue', linewidths=2)

    plot_line_collection(line_collection)
