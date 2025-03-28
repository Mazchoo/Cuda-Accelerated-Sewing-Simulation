""" Module that contains relationships between vertices of a clothing piece """
import numpy as np


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
