''' Class to store the motion matrix '''
from typing import Tuple

from pyrr import matrix44
import numpy as np
from OpenGL.GL import glUniformMatrix4fv, GL_FALSE

from src.qt.gl_helpers.uniforms import bind_globals_to_object, get_global_object_id


class Motion:
    ''' Stores the position and orientation of a single object '''
    __slots__ = 'angles', 'position', '_angle_matrix', '_position_matrix', \
                'object_id', 'motion_matrix', "globals"

    def __init__(self, position: Tuple[float, float, float],
                 angles: Tuple[float, float, float], **globals):

        self.object_id = None
        self.globals = globals
        self.angles = angles
        self.position = position

        self._angle_matrix = np.identity(4, dtype=np.float32)
        self._position_matrix = np.identity(4, dtype=np.float32)

        self.recalculate_motion_matrix(True, True)

    def increment_angles(self, xy=None, yz=None, xz=None):
        '''
            Make an adjustment to the euler angles of the object
            Call recalculate_motion_matrix (angles=True) afterwards to push change
        '''
        if yz:
            self.angles[0] += yz
            if self.angles[0] > 2 * np.pi or self.angles[0] < -2 * np.pi:
                self.angles[0] = 0
        if xy:
            self.angles[1] += xy
            if self.angles[1] > 2 * np.pi or self.angles[1] < -2 * np.pi:
                self.angles[1] = 0
        if xz:
            self.angles[2] += xz
            if self.angles[2] > 2 * np.pi or self.angles[2] < -2 * np.pi:
                self.angles[2] = 0

    def increment_position(self, x=None, y=None, z=None):
        '''
            Make an adjustment to the 3D position of the object
            Call recalculate_motion_matrix (position=True) afterwards to push change
        '''
        if x:
            self.position[0] += x
        if y:
            self.position[1] += y
        if z:
            self.position[2] += z

    def recalculate_motion_matrix(self, position: bool = True, angles: bool = True):
        ''' Recalculate the motion matrix, position and/or angles should be set to true '''
        if not position and not angles:
            return

        if position:
            self._position_matrix[3, :3] = self.position

        if angles:
            self._angle_matrix = matrix44.create_from_eulers(
                eulers=self.angles,
                dtype=np.float32
            )

        self.motion_matrix = self._angle_matrix @ self._position_matrix
        return self.motion_matrix

    def set_all_globals(self, shader: int = None, var_name: str = None):
        ''' Copy object motion matrix to the GPU '''
        glob_id = get_global_object_id(self, "object_id", shader, var_name)
        glUniformMatrix4fv(glob_id, 1, GL_FALSE, self.motion_matrix)

    def bind_global_variable_names(self, shader: int):
        ''' Bind motion matrix to id on the GPU '''
        bind_globals_to_object(self, shader)
