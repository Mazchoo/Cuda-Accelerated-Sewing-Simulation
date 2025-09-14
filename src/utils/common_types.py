"""Defines shorthand types used throughout"""

from typing import Tuple

Point2D = Tuple[float, float]
Texture2D = Tuple[float, float]  # Should all be in the range (0.-1.)
Point3D = Tuple[float, float, float]
Color3D = Tuple[float, float, float]  # Should all be in the range (0.-1.)
TriangleIndicies = Tuple[int, int, int]
