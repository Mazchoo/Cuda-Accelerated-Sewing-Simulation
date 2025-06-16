""" Class containing information to simulate clothing as one mesh """
from typing import Dict
from copy import deepcopy

import numpy as np

from src.simulation.mesh import MeshData
from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.sewing_constraints import SewingConstraints


def get_offset_copy(arr: np.ndarray, offset: int) -> np.ndarray:
    """ Return an offset copy of a numpy integer array """
    arr_copy = arr.copy()
    arr_copy += offset
    return arr_copy


class DynamicClothing:
    """
        Manages physics of simulation
        Puts all pieces into a single array of positions
    """
    def __init__(self, pieces: Dict[str, DynamicPiece],
                 sewing_constraints: SewingConstraints):
        current_offset = 0
        self.piece_to_array_offset = {}

        all_vertices = []
        all_indices = []
        all_textures = []

        all_stress_relations = []
        all_shear_relations = []
        all_bend_relations = []

        for piece_name, piece in pieces:
            self.piece_to_array_offset[piece_name] = current_offset

            all_vertices.append(piece.mesh.vertex_data.copy())
            all_indices.append(get_offset_copy(piece.mesh.index_data, current_offset))
            all_stress_relations.append(get_offset_copy(piece.vertex_relations.stress_relations, current_offset))
            all_shear_relations.append(get_offset_copy(piece.vertex_relations.shear_relations, current_offset))
            all_bend_relations.append(get_offset_copy(piece.vertex_relations.bend_relations, current_offset))

            texture_data = deepcopy(piece.mesh.texture_data)
            for texture in texture_data:
                texture['offset'] += current_offset
            all_textures.extend(texture_data)

            current_offset += len(piece.mesh.vertices)

        self.velocity = np.zeros((current_offset, 3), dtype=np.float32)
        self.acceleration = np.zeros((current_offset, 3), dtype=np.float32)

        self.mesh = MeshData(
            np.array(all_vertices, dtype=np.float32),
            np.array(all_indices, dtype=np.int32),
            all_textures
        )
