import numpy as np

from python_src.componentLibrary.math import Vector3


class component:
    def __init__(self):
        self.component_rotation_matrix = np.eye(3)
        self.vec_component_absolute_position = Vector3.Zero
        