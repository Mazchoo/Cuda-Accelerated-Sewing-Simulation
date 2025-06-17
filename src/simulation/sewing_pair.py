''' Calculate sewing relationship adjustment and store its state '''
# ToDo - Consider removing state from class
import numpy as np

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
        self.adjustment *= 0

        from_vertices = all_from_vertices[self.indices[:, 0]]
        to_vertices = all_to_vertices[self.indices[:, 1]]

        vector = to_vertices - from_vertices
        distance = np.linalg.norm(vector, axis=1, keepdims=True)
        vector /= np.where(distance == 0, 1, distance)
        adjustment_amount = np.minimum(SEWING_ADJUSTMENT_STEP * TIME_DELTA, distance) / 2

        self.adjustment += vector * adjustment_amount
