''' Container for 4by4 matrix representing camera projection '''
from typing import Optional, Dict
from numpy import ndarray

from pyrr import matrix44
import numpy as np
from OpenGL.GL import glUniformMatrix4fv, GL_FALSE

from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable


class Camera(OpenGLUploadable):
    ''' Stores and recalculates a 4x4 perspective projection matrix and can store it on GPU '''

    __slots__ = 'fovy', 'aspect', 'near', 'far', 'object_id', '_projection_matrix', 'globals'
    fovy: float
    aspect: float
    near: float
    far: float

    object_id: Optional[int]
    globals: Dict[str, str]

    _projection_matrix: ndarray

    def __init__(self, fovy: float, aspect: float, near: float, far: float, **globals):
        '''
            fovy: The vertical field of view angle in degrees
            aspect: The aspect ratio (width/height) of the viewport
            near: The distance to the near clipping plane (z is mapped to the valid range [-1, 1])
            far: The distance to the far clipping plane (z is mapped to the valid range [-1, 1])
        '''
        self.object_id = None
        self.globals = globals

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

        self._projection_matrix = matrix44.create_perspective_projection(
            fovy=fovy, aspect=aspect, near=near, far=far, dtype=np.float32
        )

    def set_all_globals(self):
        ''' Update all player properties on the GPU '''
        glUniformMatrix4fv(self.object_id, 1, GL_FALSE, self._projection_matrix)
