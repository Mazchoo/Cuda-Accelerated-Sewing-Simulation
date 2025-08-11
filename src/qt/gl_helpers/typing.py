''' Custom types for Open GL interaction '''
from typing import Tuple

import numpy as np

Position3D = Tuple[float, float, float]
Angles3D = Tuple[float, float, float]  # Euler angles
ColorRGB = Tuple[float, float, float]  # Expect each float to be in range [0., 1.]
Matrix4x4 = np.ndarray
