""" Module that contains relationships between vertices of a clothing piece """
import numpy as np
from matplotlib.collections import LineCollection


class VertexRelations:
    """
        Container class of pre-computed indices representing
        1. Stress: horizontal and vertical relationships between neighbours
        2. Shear: diagonal relationships between neightbours
        3. Bend: horizontal and vertical vertices between two neighbours

        Data contains integers references of vertex data
    """
    def __init__(self, stress_relations: np.ndarray,
                 shear_relations: np.ndarray, bend_relations: np.ndarray):
        self.stress_relations = stress_relations
        self.shear_relations = shear_relations
        self.bend_relations = bend_relations

    def stress_line_collection(self, vertices: np.ndarray, **kwargs) -> LineCollection:
        """ Create matplotlib line collection of all stress relationships """
        lines = np.stack([
            vertices[self.stress_relations[:, 0]],
            vertices[self.stress_relations[:, 1]]
        ], axis=1)

        return LineCollection(lines, **kwargs)

    def shear_line_collection(self, vertices: np.ndarray, **kwargs) -> LineCollection:
        """ Create matplotlib line collection of all shear relationships """
        lines = np.stack([
            vertices[self.shear_relations[:, 0]],
            vertices[self.shear_relations[:, 1]]
        ], axis=1)

        return LineCollection(lines, **kwargs)

    def bend_line_collection(self, vertices: np.ndarray, **kwargs) -> LineCollection:
        """ Create matplotlib line collection of all bend relationships """
        lines = np.stack([
            vertices[self.bend_relations[:, 0]],
            vertices[self.bend_relations[:, 2]]
        ], axis=1)

        return LineCollection(lines, **kwargs)
