''' Handles calculation of sewing forces between pieces '''
from typing import List

import numpy as np


class SewingPairRelations:
    """ Contains vertex indices for two pieces in a sewing relation """
    def __init__(self, from_piece: str, from_indices: np.ndarray,
                 to_piece: str, to_indices: np.ndarray):
        self.from_piece = from_piece
        self.from_indices = from_indices
        self.to_piece = to_piece
        self.to_indices = to_indices

        if len(from_indices) != len(to_indices):
            raise ValueError(f"Lengths of sewing vertices not the same {len(from_indices)} != {len(to_indices)}")

        self.forces = np.zeros(len(from_indices), dtype=np.float64)


class SewingForces:
    """ Calculates resultant forces for a piece resulting from sewing """
    def __init__(self, relations: List[SewingPairRelations]):
        self.relations = relations
