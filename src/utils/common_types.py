"""Defines shorthand types used throughout"""

from typing import Tuple, NamedTuple, List

import numpy as np


Point2D = Tuple[float, float]
Texture2D = Tuple[float, float]  # Should all be in the range (0.-1.)
Point3D = Tuple[float, float, float]
Color3D = Tuple[float, float, float]  # Should all be in the range (0.-1.)
TriangleIndicies = Tuple[int, int, int]


class TriangleMeshArrays(NamedTuple):
    """Holds the information in numpy to draw a mesh"""

    vertex_data: (
        np.ndarray
    )  # float32, nr_vertices by 8, 3 for position, 2 for texture and 3 for normal
    index_data: np.ndarray  # uint32, nr_triangles by 3, one for each vertex
    texture_data: List[dict]  # texture_data for material drawing pass
