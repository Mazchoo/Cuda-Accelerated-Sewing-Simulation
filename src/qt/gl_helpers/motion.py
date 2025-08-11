''' Class to store the motion matrix '''
from typing import Optional, Dict

from pyrr import matrix44
import numpy as np
from OpenGL.GL import glUniformMatrix4fv, GL_FALSE

from src.qt.gl_helpers.shader_program import ShaderProgram
from src.qt.gl_helpers.uniforms import bind_globals_to_object, get_global_object_id
from src.qt.gl_helpers.typing import Matrix4x4, Angles3D, Position3D


class Motion:
    ''' Stores the position and orientation of a single object '''
    __slots__ = '_angles', '_position', '_angle_matrix', '_position_matrix', \
                'object_id', 'motion_matrix', "globals"

    object_id: Optional[int]
    motion_matrix: Matrix4x4
    globals: Dict[str, str]

    _angles: Angles3D
    _position: Position3D
    _angle_matrix: Matrix4x4
    _position_matrix: Matrix4x4

    def __init__(self, position: Position3D = (0., 0., 0.),
                 angles: Angles3D = (0., 0., 0.), **globals):
        """
        Initialize a Motion object with position and orientation.

        Args:
            position: 3D position as (x, y, z) tuple
            angles: 3D Euler angles as (pitch, yaw, roll) tuple in radians
            **globals: Global variable mappings for shader uniforms
        """
        self.object_id = None
        self.globals = globals
        self._angles = angles
        self._position = position

        self._angle_matrix = np.identity(4, dtype=np.float32)
        self._position_matrix = np.identity(4, dtype=np.float32)

        self.recalculate_motion_matrix()

    def increment_angles(self, xy: Optional[float] = None,
                         yz: Optional[float] = None, xz: Optional[float] = None):
        """
        Make an adjustment to the euler angles of the object.
        Call recalculate_motion_matrix(angles=True) afterwards to push change.

        Args:
            xy: Rotation around X-Y plane (pitch) in radians
            yz: Rotation around Y-Z plane (yaw) in radians
            xz: Rotation around X-Z plane (roll) in radians
        """
        if yz is not None:
            self._angles = (
                self._angles[0] + yz,
                self._angles[1],
                self._angles[2]
            )
            if self._angles[0] > 2 * np.pi or self._angles[0] < -2 * np.pi:
                self._angles = (0.0, self._angles[1], self._angles[2])

        if xy is not None:
            self._angles = (
                self._angles[0],
                self._angles[1] + xy,
                self._angles[2]
            )
            if self._angles[1] > 2 * np.pi or self._angles[1] < -2 * np.pi:
                self._angles = (self._angles[0], 0.0, self._angles[2])

        if xz is not None:
            self._angles = (
                self._angles[0],
                self._angles[1],
                self._angles[2] + xz
            )
            if self._angles[2] > 2 * np.pi or self._angles[2] < -2 * np.pi:
                self._angles = (self._angles[0], self._angles[1], 0.0)

    def increment_position(self, x: Optional[float] = None,
                           y: Optional[float] = None, z: Optional[float] = None):
        """
        Make an adjustment to the 3D position of the object.
        Call recalculate_motion_matrix(position=True) afterwards to push change.

        Args:
            x: Translation along X-axis
            y: Translation along Y-axis
            z: Translation along Z-axis
        """
        if x is not None:
            self._position = (self._position[0] + x, self._position[1], self._position[2])
        if y is not None:
            self._position = (self._position[0], self._position[1] + y, self._position[2])
        if z is not None:
            self._position = (self._position[0], self._position[1], self._position[2] + z)

    def recalculate_motion_matrix(self, position: bool = True, angles: bool = True) -> Matrix4x4:
        """
            Recalculate the motion matrix, position and/or angles should be set to true.
            Returns the recalculated 4x4 motion matrix
        """
        if not position and not angles:
            return self.motion_matrix

        if position:
            self._position_matrix[3, :3] = self._position

        if angles:
            self._angle_matrix = matrix44.create_from_eulers(
                eulers=self._angles,
                dtype=np.float32
            )

        self.motion_matrix = self._angle_matrix @ self._position_matrix
        return self.motion_matrix

    def set_all_globals(self):
        """ Copy object motion matrix to the GPU. """
        glob_id = get_global_object_id(self, "object_id")
        glUniformMatrix4fv(glob_id, 1, GL_FALSE, self.motion_matrix)

    def bind_global_variable_names(self, shader: ShaderProgram):
        """ Bind motion matrix to id on the GPU. """
        shader.use()
        bind_globals_to_object(self, shader.gl_id)
        self.set_all_globals()
