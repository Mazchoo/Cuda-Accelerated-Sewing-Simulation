""" Convert contours of clothing to grid of points """
from typing import List, Optional, Dict, Tuple

import numpy as np
from shapely.geometry import Polygon, Point

from src.utils.file_io import read_json
from src.utils.geometry import length_along_contour, points_along_contour
from src.utils.read_obj import parse_obj

from src.simulation.mesh import MeshData, get_annotation_dict_from_piece_data
from src.simulation.setup.alignment import snap_and_align_piece_to_body
from src.simulation.setup.vertex_relationships import VertexRelations
from src.simulation.setup.bend_piece_over_body import bend_piece_over_body
from src.simulation.piece_physics import DynamicPiece
from src.simulation.sewing_forces import SewingPairRelations, SewingForces

from src.parameters import VERTEX_RESOLUTION, CM_PER_M, SEWING_SPACING, AVATAR_SCALING


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

    turn_points = np.array(
        [[x, y, 0] for x, y in piece_data["turn_points"]], dtype=np.float32
    )

    mesh = MeshData(
        np.array(vertex_data, dtype=np.float32) / CM_PER_M,
        np.array(faces, dtype=np.uint32),
        texture_data,
        annotations=get_annotation_dict_from_piece_data(piece_data),
        turn_points=turn_points / CM_PER_M
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


def get_sewing_range(piece_mesh: MeshData, sewing_entry: dict) -> \
                     Tuple[np.ndarray, np.ndarray, float, float]:
    """ Get sewing range in terms of [point start, point end, start marker, end marker] """
    tp_start = piece_mesh.get_turn_point_by_ind(sewing_entry["tp_index_start"])
    tp_end = piece_mesh.get_turn_point_by_ind(sewing_entry["tp_index_end"])
    return tp_start, tp_end, sewing_entry["marker_start"], sewing_entry["marker_end"]


def get_offset_contour_3d(piece_mesh: MeshData, piece_data: dict) -> np.ndarray:
    """ Get contour from clothing data in 3d coordinates """
    contour = np.array([[x, y, 0] for x, y in piece_data["contour"]], dtype=np.float64) / CM_PER_M
    contour -= piece_mesh.origin_array
    return Polygon(contour).exterior


def get_indices_of_closest_points_in_mesh(piece_mesh: MeshData, sewing_points: np.ndarray) -> np.ndarray:
    """ Given 2d sewing points find the indices in the mesh of the closest vertices (assumes mesh has z=0) """
    # ToDo - when optimising figure out contour indices at the beginning will make this O(n) search in terms of resolution
    vertices = piece_mesh.vertices_2d
    output = []
    for pt in sewing_points:
        output.append(np.linalg.norm(vertices - pt, axis=1).argmin())

    return np.array(output, dtype=np.uint32)


def get_indices_for_one_sewing_pair(sewing_pair: dict, pieces: Dict[str, DynamicPiece],
                                    clothing_data: dict) -> SewingPairRelations:
    """ Extract sewing pair of interacting vertices for one sewing entry """
    from_piece_name = sewing_pair["from"]["piece"]
    from_piece_mesh = pieces[from_piece_name].mesh
    from_range = get_sewing_range(from_piece_mesh, sewing_pair["from"])
    from_contour = get_offset_contour_3d(from_piece_mesh, clothing_data["pieces"][from_piece_name])
    from_sewing_length = length_along_contour(from_contour, *from_range)

    to_piece_name = sewing_pair["to"]["piece"]
    to_piece_mesh = pieces[to_piece_name].mesh
    to_range = get_sewing_range(to_piece_mesh, sewing_pair["to"])
    to_contour = get_offset_contour_3d(to_piece_mesh, clothing_data["pieces"][to_piece_name])
    to_sewing_length = length_along_contour(to_contour, *to_range)

    average_length = (to_sewing_length + from_sewing_length) / 2

    nr_sewing_points = int(average_length / SEWING_SPACING)

    from_points = points_along_contour(from_contour, *from_range, nr_sewing_points)
    from_points_2d = np.array([[p.x, p.y] for p in from_points], dtype=np.float32)
    from_sewing_indices = get_indices_of_closest_points_in_mesh(from_piece_mesh, from_points_2d)

    to_points = points_along_contour(to_contour, *to_range, nr_sewing_points)
    to_points_2d = np.array([[p.x, p.y] for p in to_points], dtype=np.float32)
    to_sewing_indices = get_indices_of_closest_points_in_mesh(to_piece_mesh, to_points_2d)

    return SewingPairRelations(from_piece_name, from_sewing_indices, to_piece_name, to_sewing_indices)


def extract_all_piece_vertices(clothing_data: dict,
                               body_mesh: Optional[MeshData] = None) -> Tuple[Dict[str, DynamicPiece], SewingForces]:
    """ Get piece simulation and display data from every piece in clothing data """
    output = {}

    for key, piece_data in clothing_data["pieces"].items():
        vertices_by_line = extract_grid(piece_data)
        mesh, grid_indices = convert_rows_of_vertices_into_triangles(vertices_by_line, piece_data)
        vertex_relations = get_all_vertex_relationships(vertices_by_line, grid_indices)
        output[key] = DynamicPiece(mesh, vertex_relations,
                                   piece_data["body_points"]["snap"]["name"],
                                   piece_data["body_points"]["alignment"]["name"])

    all_sewing = [
        get_indices_for_one_sewing_pair(sew_pair, output, clothing_data) for sew_pair in clothing_data["sewing"]
    ]
    sewing_forces = SewingForces(all_sewing)

    if body_mesh is not None:
        for key, new_piece in output.items():
            snap_and_align_piece_to_body(new_piece, body_mesh)

            if clothing_data["pieces"][key].get("wraps_around_body"):
                bend_piece_over_body(new_piece, body_mesh, VERTEX_RESOLUTION / CM_PER_M)

            new_piece.body_collision_adjustment(body_mesh.trimesh)

    return output, sewing_forces


if __name__ == '__main__':
    clothing_data = read_json('./assets/sewing_shirt.json')
    avatar_mesh = parse_obj('./assets/BodyMesh.obj', './assets/BodyAnnotations.json')
    avatar_mesh.scale_vertices(AVATAR_SCALING)
    extract_all_piece_vertices(clothing_data, avatar_mesh)
