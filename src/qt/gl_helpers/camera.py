''' Container for 4by4 matrix representing camera projection '''
from typing import Optional

from pyrr import matrix44
import numpy as np


class Camera:
    ''' Stores and recalculates a 4x4 perspective projection matrix and can store it on GPU '''

    __slots__ = 'fovy', 'aspect', 'near', 'far', 'object_id', 'projection_matrix', 'globals'

    def __init__(self, fovy: float, aspect: float, near: float, far: float):
        '''
            fovy: The vertical field of view angle in degrees
            aspect: The aspect ratio (width/height) of the viewport
            near: The distance to the near clipping plane (z is mapped to the valid range [-1, 1])
            far: The distance to the far clipping plane (z is mapped to the valid range [-1, 1])
        '''
        self.fovy = fovy
        self.aspect = aspect
        self.near = near
        self.far = far

        self.recalculate_projection(fovy, aspect, near, far)

    def recalculate_projection(self, fovy: Optional[float] = None, aspect: Optional[float] = None,
                               near: Optional[float] = None, far: Optional[float] = None):
        ''' Recalcuate projection matrix, incorporating any changes '''
        fovy = fovy or self.fovy
        aspect = aspect or self.aspect
        near = near or self.near
        far = far or self.far

        self.projection_matrix = matrix44.create_perspective_projection(
            fovy=fovy, aspect=aspect, near=near, far=far, dtype=np.float32
        )
