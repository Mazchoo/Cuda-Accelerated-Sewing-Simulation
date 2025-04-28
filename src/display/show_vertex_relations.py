""" Module to display vertex relationships as line collections """
from src.utils.file_io import read_json
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices

from src.display.common import plot_line_collection


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data, _ = extract_all_piece_vertices(clothing_data)

    vertices = clothing_display_data["L-1"].mesh.vertices_2d
    vertex_relations = clothing_display_data["L-1"].vertex_relations

    stress_lines = vertex_relations.stress_line_collection(vertices, colors='blue', linewidths=4)
    shear_lines = vertex_relations.shear_line_collection(vertices, colors='red', linewidths=1)
    bend_lines = vertex_relations.bend_line_collection(vertices, colors='green', linewidths=2)

    plot_line_collection(stress_lines, shear_lines, bend_lines)
