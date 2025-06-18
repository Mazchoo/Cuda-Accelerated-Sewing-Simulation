''' Handles calculation of sewing forces between pieces '''
from typing import List, Iterator, Dict

from src.simulation.common import DistanceAdjustment
from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.sewing_pair import SewingPairRelations


class SewingConstraints:
    """ Calculates resultant adjustment for a piece resulting from sewing """
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
