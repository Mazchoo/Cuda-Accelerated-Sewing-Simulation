""" Class containing information to place a piece """
import numpy as np

from src.simulation.mesh import MeshData
from src.simulation.setup.vertex_relationships import VertexRelations


class DynamicPiece:
    """ Piece placement helpers """
    def __init__(self, mesh: MeshData, vertex_relations: VertexRelations,
                 snap_point_name: str, alignment_point_name: str):
        self.mesh = mesh
        self.vertex_relations = vertex_relations

        self._snap_point_name = snap_point_name
        self._alignment_point_name = alignment_point_name

    @property
    def snap_point(self) -> np.ndarray:
        """ Return point to snap to body by offset """
        return self.mesh.get_annotation(self._snap_point_name)

    @property
    def snap_point_name(self) -> str:
        """ Get name of point to snap to on body by offset """
        return self._snap_point_name

    @property
    def alignment_point(self) -> np.ndarray:
        """ Return point to rotate other point to so matches orientation of body
            i.e. snap to alignment vector on piece matches snap to alignment on body """
        return self.mesh.get_annotation(self._alignment_point_name)

    @property
    def alignment_point_name(self) -> str:
        """ Get name of alignment point """
        return self._alignment_point_name

    @property
    def align_vector(self) -> np.ndarray:
        """ Get alignment vector from snap-point to alignment point """
        return self.alignment_point - self.snap_point
