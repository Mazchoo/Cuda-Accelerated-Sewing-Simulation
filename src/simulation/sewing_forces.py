''' Handles calculation of sewing forces between pieces '''
from typing import List, Iterator, Dict

import numpy as np

from src.simulation.common import DistanceAdjustment
from src.simulation.piece_physics import DynamicPiece

from src.parameters import SEWING_ADJUSTMENT_STEP, TIME_DELTA


class SewingPairRelations:
    """ Contains vertex indices for two pieces in a sewing relation """
    def __init__(self, from_piece: str, from_indices: np.ndarray,
                 to_piece: str, to_indices: np.ndarray):
        self.from_piece = from_piece
        self.to_piece = to_piece

        if len(from_indices) != len(to_indices):
            raise ValueError(f"Lengths of sewing vertices not the same {len(from_indices)} != {len(to_indices)}")

        self.indices = np.array(list(zip(from_indices, to_indices)), dtype=np.uint32)
        self.adjustment = np.zeros((len(self.indices), 3), dtype=np.float64)  # applied in direction from to

    def recalculate_adjustment(self, all_from_vertices: np.ndarray, all_to_vertices: np.ndarray):
        """
            Give vertices of two pieces involved find the adjustment to move vertices closer
            The adjustment amount is capped at SEWING_ADJUSTMENT_STEP in magnitude
        """
        # ToDo - target for optimising if using references to store relations instead
        self.adjustment *= 0

        from_vertices = all_from_vertices[self.indices[:, 0]]
        to_vertices = all_to_vertices[self.indices[:, 1]]

        vector = to_vertices - from_vertices
        distance = np.linalg.norm(vector, axis=1, keepdims=True)
        vector /= np.where(distance == 0, 1, distance)
        adjustment_amount = np.minimum(SEWING_ADJUSTMENT_STEP * TIME_DELTA, distance) / 2

        self.adjustment += vector * adjustment_amount


class SewingForces:
    """ Calculates resultant forces for a piece resulting from sewing """
    def __init__(self, relations: List[SewingPairRelations]):
        self.relations = relations

    def recalculate_adjustment(self, dynamic_pieces: Dict[str, DynamicPiece]):
        """ Calculate in place to position adjustments for each sewing pair """
        for sewing_pair in self:
            from_vertices = dynamic_pieces[sewing_pair.from_piece].mesh.vertices_3d
            to_vertices = dynamic_pieces[sewing_pair.to_piece].mesh.vertices_3d
            sewing_pair.recalculate_adjustment(from_vertices, to_vertices)

    def get_adjustment_for_piece(self, piece_name: str) -> DistanceAdjustment:
        indices, amounts = [], []
        for sewing_pair in self:
            if sewing_pair.from_piece == piece_name:
                indices.append(sewing_pair.indices[:, 0])
                amounts.append(sewing_pair.adjustment)

            if sewing_pair.to_piece == piece_name:
                indices.append(sewing_pair.indices[:, 1])
                amounts.append(-sewing_pair.adjustment)

        return DistanceAdjustment(indices, amounts)

    def __iter__(self) -> Iterator[SewingPairRelations]:
        """ Iterate through all sewing pairs """
        yield from self.relations

    def __len__(self) -> int:
        """ Get number of sewing pairs """
        return len(self.relations)
