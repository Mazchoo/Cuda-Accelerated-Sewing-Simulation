""" Functions that fuse vertex data and piece relationships """
from typing import Dict, Tuple, List
from copy import deepcopy

import numpy as np
from trimesh import Trimesh

from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.sewing_constraints import SewingConstraints

PieceIndexRanges = Dict[str, Tuple[int, int]]


def get_offset_copy(arr: np.ndarray, offset: int) -> np.ndarray:
    """ Return an offset copy of a numpy integer array """
    arr_copy = arr.copy()
    arr_copy += offset
    return arr_copy


def get_piece_to_index_range_mapping(pieces: Dict[str, DynamicPiece]) -> PieceIndexRanges:
    """ Get array range in dictionary order """
    piece_to_index_range = {}
    current_offset = 0

    for piece_name, piece in pieces.items():
        piece_to_index_range[piece_name] = (current_offset, current_offset + len(piece.mesh))
        current_offset += len(piece.mesh)

    return piece_to_index_range


def get_combined_vertex_data(pieces: Dict[str, DynamicPiece],
                             index_ranges: PieceIndexRanges) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
        Combine the vertex information, triangle and texture information for
        multiple pieces using pre-calculated index ranges
    """
    all_vertices = []
    all_indices = []
    all_textures = []

    for piece_name, piece in pieces.items():
        start_ind, _ = index_ranges[piece_name]
        all_vertices.append(piece.mesh.vertex_data.copy())
        all_indices.append(get_offset_copy(piece.mesh.index_data, start_ind))

        texture_data = deepcopy(piece.mesh.texture_data)
        for texture in [t for t in texture_data if isinstance(t, dict)]:
            texture['offset'] += start_ind
        all_textures.extend(texture_data)

    return (np.concatenate(all_vertices, dtype=np.float32),
            np.concatenate(all_indices, dtype=np.uint32),
            all_textures)


def get_combined_particle_relations(pieces: Dict[str, DynamicPiece],
                                    index_ranges: PieceIndexRanges) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
        Combine stress, shear and bend relations for each piece
        multiple pieces using pre-calculated index ranges
    """
    all_stress_relations = []
    all_shear_relations = []
    all_bend_relations = []

    for piece_name, piece in pieces.items():
        start_ind, _ = index_ranges[piece_name]

        all_stress_relations.append(get_offset_copy(piece.vertex_relations.stress_relations, start_ind))
        all_shear_relations.append(get_offset_copy(piece.vertex_relations.shear_relations, start_ind))
        all_bend_relations.append(get_offset_copy(piece.vertex_relations.bend_relations, start_ind))

    return (np.concatenate(all_stress_relations),
            np.concatenate(all_shear_relations),
            np.concatenate(all_bend_relations))


def get_combined_sewing_relations(sewing_constraints: SewingConstraints,
                                  index_ranges: PieceIndexRanges) -> Tuple[np.ndarray, np.ndarray]:
    """
        Combine sewing index relationships going from using global indices
    """
    all_from_indices = []
    all_to_indices = []

    for sewing_pair in sewing_constraints:
        from_start_ind, _ = index_ranges[sewing_pair.from_piece]
        all_from_indices.append(get_offset_copy(sewing_pair.indices[:, 0], from_start_ind))

        to_start_ind, _ = index_ranges.get(sewing_pair.to_piece)
        all_to_indices.append(get_offset_copy(sewing_pair.indices[:, 1], to_start_ind))

    return np.concatenate(all_from_indices), np.concatenate(all_to_indices)


def get_body_mesh_arrays(trimesh: Trimesh) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
        Extract array information from trimesh into numpy arrays
        (n, 3, 3) float arrays of triangle 3d vertex triplets, in p0, p0 -> p1, p0 -> p2 format
        (n, 4) centers of each triangle + distance to center
        (n, 3) normals of each triangle
    """
    triangles = np.array([
        [trimesh.vertices[i], trimesh.vertices[j], trimesh.vertices[k]] for i, j, k in trimesh.faces
    ], dtype=np.float32)
    triangles[:, 1] -= triangles[:, 0]
    triangles[:, 2] -= triangles[:, 0]

    centers = (triangles[:, 0] + triangles[:, 1] + triangles[:, 2]) / 3
    distances_to_center = np.expand_dims(np.max(
        np.linalg.norm(triangles - np.expand_dims(centers, 1), axis=2), axis=1
    ), axis=-1)
    centers = np.hstack([centers, distances_to_center])

    return triangles, centers, trimesh.face_normals.astype(np.float32)
