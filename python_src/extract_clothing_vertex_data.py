""" Convert contours of clothing to grid of points """
from typing import List, Optional

import numpy as np
from shapely.geometry import Polygon, Point

from python_src.utils.file_io import read_json

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


def convert_rows_of_vertices_into_triangles(vertices_by_line: List[List[Optional[np.ndarray]]]):
    """ Get 3d drawing information from a grid of points inside the contour """
    vertex_data = []
    faces = []
    next_vertex_data_ind = np.int32(0)
    vertex_indices = np.zeros((len(vertices_by_line), len(vertices_by_line[0])), dtype=np.int32)

    for i, row in enumerate(vertices_by_line):
        for j, vertex in enumerate(row):
            if vertex is None:
                continue
            vertex_row = [vertex[0], vertex[1], 0.]  # ToDo Could have texture data / normal as well

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

    return np.array(vertex_data, dtype=np.float32), np.array(faces, dtype=np.int32)


def extract_all_piece_vertices(clothing_data: dict):
    """ Get piece simulation and display data from every piece in clothing data """
    output = {}

    for key, piece_data in clothing_data["pieces"].items():
        vertices_by_line = extract_grid(piece_data)
        vertex_data, index_data = convert_rows_of_vertices_into_triangles(vertices_by_line)
        output[key] = {"vertex_data": vertex_data, "index_data": index_data}

    return output


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    extract_all_piece_vertices(clothing_data)
