
from typing import Optional, Tuple, Dict

import numpy as np
import pyrr
from OpenGL.GL import glUniformMatrix4fv, GL_FALSE

from src.qt.gl_helpers.camera import Camera
from src.qt.gl_helpers.uniforms import bind_globals_to_object, get_global_object_id


class Player:
    __slots__ = '_position', '_theta', '_phi', '_position_matrix', \
        '_angle_matrix', '_view_matrix', 'camera', 'object_id', 'globals'

    camera: Camera
    object_id: Optional[int]
    globals: Dict[str, str]

    _position: np.ndarray
    _theta: float
    _phi: float
    _position_matrix: np.ndarray
    _angle_matrix: np.ndarray
    _view_matrix: np.ndarray

    def __init__(self, camera: Camera, theta: float = 0., phi: float = 0.,
                 position: Tuple[float, float, float] = (0., 0., 0.), **globals):
        self.camera = camera
        self._position = position
        self._theta = theta
        self._phi = phi

        self.object_id = None
        self.globals = globals

        self._position = np.array(position, dtype=np.float32)

        self._position_matrix = np.identity(4, dtype=np.float32)
        self._angle_matrix = np.identity(4, dtype=np.float32)

        self.recalculate_player_view(position=True, theta=True, phi=True)

    def increment_angles(self, theta: Optional[float] = None, phi: Optional[float] = None):
        if theta:
            self._theta += theta
            if self._theta > 2 * np.pi or self._theta < -2 * np.pi:
                self._theta = 0

        if phi:
            self._phi += phi
            self._phi = np.clip(self._phi, -0.5 * np.pi, 0.5 * np.pi)

    def set_angles(self, theta: Optional[float] = None, phi: Optional[float] = None):
        if theta:
            if theta > 2 * np.pi or theta < -2 * np.pi:
                theta = 0
            self._theta = theta

        if phi:
            self._phi = np.clip(phi, -0.5 * np.pi, 0.5 * np.pi)

    def increment_position(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        if x:
            self._position[0] += x
        if y:
            self._position[1] += y
        if z:
            self._position[2] += z

    def set_position(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        if x:
            self._position[0] = x
        if y:
            self._position[1] = y
        if z:
            self._position[2] = z

    def recalculate_player_view(self, position: bool = False, theta: bool = False, phi: bool = False):
        if position:
            self._position_matrix[3, :3] = self._position

        if theta or phi:
            self._angle_matrix = pyrr.matrix44.create_from_eulers(
                eulers=[self._phi, 0, self._theta],
                dtype=np.float32
            )

        self._view_matrix = self._position_matrix @ self._angle_matrix

    def set_all_globals(self, shader: Optional[int] = None, var_name: Optional[str] = None):
        glob_id = get_global_object_id(self, "object_id", shader, var_name)
        glUniformMatrix4fv(glob_id, 1, GL_FALSE, self._view_matrix)

    def bind_global_variable_names(self, shader: int):
        bind_globals_to_object(self, shader)
        self.camera.bind_global_variable_names(shader)
