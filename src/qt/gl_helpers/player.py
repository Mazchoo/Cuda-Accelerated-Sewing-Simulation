''' Container for 4x4 matrix representing player view transformation '''

from typing import Optional, Dict

import numpy as np
from pyrr import matrix44
from OpenGL.GL import glUniformMatrix4fv, GL_FALSE

from src.qt.gl_helpers.camera import Camera
from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable
from src.qt.gl_helpers.typing import Matrix4x4, Position3D


class Player(OpenGLUploadable):
    ''' Stores and recalculates a 4x4 view matrix for player perspective and can store it on GPU '''

    __slots__ = '_position', '_theta', '_phi', '_position_matrix', \
        '_angle_matrix', 'view_matrix', 'camera', 'object_id', 'globals'

    camera: Camera
    object_id: Optional[int]
    globals: Dict[str, str]
    view_matrix: Matrix4x4

    _position: np.ndarray
    _theta: float
    _phi: float
    _position_matrix: Matrix4x4
    _angle_matrix: Matrix4x4

    def __init__(self, camera: Camera, theta: float = 0., phi: float = 0.,
                 position: Position3D = (0., 0., 0.), **globals):
        ''' Initialize player view transformation '''
        self.camera = camera
        self.object_id = None
        self.globals = globals

        self._theta = theta
        self._phi = phi
        self._position = np.array(position, dtype=np.float32)

        self._position_matrix = np.identity(4, dtype=np.float32)
        self._angle_matrix = np.identity(4, dtype=np.float32)

        self.recalculate_player_view(position=True, theta=True, phi=True)

    def increment_angles(self, theta: Optional[float] = None, phi: Optional[float] = None):
        ''' Increment the player's viewing angles. Requires recalculate to update matrix. '''
        if theta:
            self._theta += theta
            if self._theta > 2 * np.pi or self._theta < -2 * np.pi:
                self._theta = 0

        if phi:
            self._phi += phi
            self._phi = np.clip(self._phi, -0.5 * np.pi, 0.5 * np.pi)

    def set_angles(self, theta: Optional[float] = None, phi: Optional[float] = None):
        ''' Set the player's viewing angles to specific values. Requires recalculate to update matrix. '''
        if theta:
            if theta > 2 * np.pi or theta < -2 * np.pi:
                theta = 0
            self._theta = theta

        if phi:
            self._phi = np.clip(phi, -0.5 * np.pi, 0.5 * np.pi)

    def increment_position(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        ''' Increment the player's position by given amounts. Requires recalculate to update matrix. '''
        if x:
            self._position[0] += x
        if y:
            self._position[1] += y
        if z:
            self._position[2] += z

    def set_position(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        ''' Set the player's position to specific coordinates. Requires recalculate to update matrix. '''
        if x:
            self._position[0] = x
        if y:
            self._position[1] = y
        if z:
            self._position[2] = z

    def recalculate_player_view(self, position: bool = True, theta: bool = True, phi: bool = True):
        '''
            Recalculate the player view matrix based on current parameters
            Atleast one of position, theta or phi must be set to True
        '''
        view = matrix44.create_look_at(
            eye=self._position,
            target=[0., self._position[1], 0.],
            up=[0., 1., 0.]
        )

        self.view_matrix = self.camera.projection_matrix @ view

    def set_all_globals(self):
        ''' Update all player properties on the GPU '''
        glUniformMatrix4fv(self.object_id, 1, GL_FALSE, self.view_matrix)
