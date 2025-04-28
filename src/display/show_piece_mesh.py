""" Show the mesh of a piece in matplotlib """
from src.utils.file_io import read_json
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices
from src.simulation.mesh import create_mesh_line_collection

from src.display.common import plot_line_collection


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data, _ = extract_all_piece_vertices(clothing_data)

    mesh = clothing_display_data["L-1"].mesh
    line_collection = create_mesh_line_collection(mesh, colors='blue', linewidths=2)

    plot_line_collection(line_collection)
