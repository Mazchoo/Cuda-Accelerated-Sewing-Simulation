""" Convert contours of clothing to grid of points """
from typing import List, Optional, Dict

import numpy as np
from shapely.geometry import Polygon, Point

from python_src.utils.file_io import read_json
from python_src.simulation.mesh import MeshData

from python_src.parameters import VERTEX_RESOLUTION


def extract_grid(piece_data: dict) -> List[List[Optional[np.ndarray]]]:
    """ Extract all points of inside shape contour in a grid, non-existent points are None """
    (min_x, min_y), (max_x, max_y) = piece_data["bounding_box"]
    x_range = np.linspace(min_x, max_x, int(np.ceil((max_x - min_x) / VERTEX_RESOLUTION)))
    y_range = np.linspace(min_y, max_y, int(np.ceil((max_x - min_x) / VERTEX_RESOLUTION)))
    all_rows = []

    polygon = Polygon(piece_data["contour"])

    for y in y_range:
        row = []

        for x in x_range:
            point = Point(x, y)
            if polygon.contains(point):
                row.append(np.array([x, y], dtype=np.float32))
            else:
                row.append(None)

        all_rows.append(row)

    return all_rows


def convert_rows_of_vertices_into_triangles(vertices_by_line: List[List[Optional[np.ndarray]]],
                                            piece_data: dict) -> MeshData:
    """ Get 3d drawing information from a grid of points inside the contour """
    vertex_data = []
    faces = []
    next_vertex_data_ind = np.int32(0)
    vertex_indices = np.zeros((len(vertices_by_line), len(vertices_by_line[0])), dtype=np.int32)

    (min_x, min_y), (max_x, max_y) = piece_data["bounding_box"]
    width = max_x - min_x
    height = max_y - min_y

    for i, row in enumerate(vertices_by_line):
        for j, vertex in enumerate(row):
            if vertex is None:
                continue
            vertex_row = [vertex[0], vertex[1], 0., vertex[0] / width, vertex[1] / height, 0., 0., 1.]

            next_vertex_data_ind += 1
            vertex_data.append(vertex_row)
            vertex_indices[i][j] = next_vertex_data_ind

            if i > 0 and j > 0:
                lower_left = vertex_indices[i - 1, j - 1]
                lower_right = vertex_indices[i - 1, j]
                upper_left = vertex_indices[i, j - 1]

                if lower_left and upper_left:
                    faces.append([next_vertex_data_ind - 1, upper_left - 1, lower_left - 1])

                if lower_left and lower_right:
                    faces.append([lower_right - 1, next_vertex_data_ind - 1, lower_left - 1])

    # Material data is just a single color for now
    texture_data = {
        (0.5, 0.5, 0.5): {'count': len(faces), 'offset': 0}
    }

    return MeshData(
        np.array(vertex_data, dtype=np.float32) / 100,
        np.array(faces, dtype=np.int32),
        texture_data
    )


def extract_all_piece_vertices(clothing_data: dict) -> Dict[str, MeshData]:
    """ Get piece simulation and display data from every piece in clothing data """
    output = {}

    for key, piece_data in clothing_data["pieces"].items():
        vertices_by_line = extract_grid(piece_data)
        mesh = convert_rows_of_vertices_into_triangles(vertices_by_line, piece_data)
        output[key] = mesh

    return output


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    extract_all_piece_vertices(clothing_data)
