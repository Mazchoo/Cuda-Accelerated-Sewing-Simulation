""" Convert contours of clothing to grid of points """
from typing import List, Optional, Dict, Tuple

import numpy as np
from shapely.geometry import Polygon, Point

from python_src.utils.file_io import read_json
from python_src.simulation.mesh import MeshData, get_annotation_dict_from_piece_data, snap_and_align_piece_to_body
from python_src.simulation.vertex_relationships import VertexRelations
from python_src.simulation.piece_physics import DynamicPiece

from python_src.parameters import VERTEX_RESOLUTION, CM_PER_M


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
                                            piece_data: dict) -> Tuple[MeshData, np.ndarray]:
    """
        Get 3d drawing information from a grid of points inside the contour\
        Return a mesh and the index relationship between a piece and its
    """
    vertex_data = []
    faces = []
    # ToDo - Extract getting vertex indices into its own method
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

    mesh = MeshData(
        np.array(vertex_data, dtype=np.float32) / CM_PER_M,
        np.array(faces, dtype=np.uint32),
        texture_data,
        annotations=get_annotation_dict_from_piece_data(piece_data)
    )
    if piece_data["body_points"]["alignment"]["flip"]:
        mesh.flip_x()

    return mesh, vertex_indices


def get_all_vertex_relationships(vertices_by_line: List[List[Optional[np.ndarray]]],
                                 grid_indices: np.ndarray) -> VertexRelations:
    """ Extract relationships between vertices  """
    stress_relations = []
    shear_relations = []
    bend_relations = []

    nr_rows = len(vertices_by_line)
    nr_cols = len(vertices_by_line[0])

    for i in range(nr_rows):
        for j in range(nr_cols):
            current_ind = grid_indices[i, j]
            lower_left = grid_indices[i - 1, j - 1] if i > 0 and j > 0 else None
            lower_middle = grid_indices[i - 1, j] if i > 0 else None
            middle_left = grid_indices[i, j - 1] if j > 0 else None
            upper_middle = grid_indices[i + 1, j] if i < nr_rows - 1 else None
            middle_right = grid_indices[i, j + 1] if j < nr_cols - 1 else None

            if current_ind:
                if lower_middle:
                    stress_relations.append([current_ind - 1, lower_middle - 1])

                    if upper_middle:
                        bend_relations.append([upper_middle - 1, current_ind - 1, lower_middle - 1])

                if middle_left:
                    stress_relations.append([current_ind - 1, middle_left - 1])

                    if middle_right:
                        bend_relations.append([middle_right - 1, current_ind - 1, middle_left - 1])

                if lower_left:
                    shear_relations.append([current_ind - 1, lower_left - 1])

            if lower_middle and middle_left:
                shear_relations.append([lower_middle - 1, middle_left - 1])

    return VertexRelations(
        np.array(stress_relations, dtype=np.uint32),
        np.array(shear_relations, dtype=np.uint32),
        np.array(bend_relations, dtype=np.uint32),
    )


def extract_all_piece_vertices(clothing_data: dict,
                               body_mesh: Optional[MeshData] = None) -> Dict[str, DynamicPiece]:
    """ Get piece simulation and display data from every piece in clothing data """
    output = {}

    for key, piece_data in clothing_data["pieces"].items():
        vertices_by_line = extract_grid(piece_data)
        mesh, grid_indices = convert_rows_of_vertices_into_triangles(vertices_by_line, piece_data)
        vertex_relations = get_all_vertex_relationships(vertices_by_line, grid_indices)
        new_piece = DynamicPiece(mesh, vertex_relations,
                                 piece_data["body_points"]["snap"]["name"],
                                 piece_data["body_points"]["alignment"]["name"])
        if body_mesh is not None:
            snap_and_align_piece_to_body(new_piece, body_mesh)

        output[key] = new_piece

    return output


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    extract_all_piece_vertices(clothing_data)
