"""Container for 4x4 matrix representing player view transformation"""

from typing import Optional, Dict

import numpy as np
from pyrr import matrix44
from OpenGL.GL import glUniformMatrix4fv, GL_FALSE

from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable
from src.qt.gl_helpers.typing import Matrix4x4, Position3D


class Player(OpenGLUploadable):
    """Stores and recalculates a 4x4 view matrix for player perspective and can store it on GPU"""

    __slots__ = (
        "_position",
        "_theta",
        "_phi",
        "_position_matrix",
        "_angle_matrix",
        "view_matrix",
        "camera",
        "object_id",
        "shader_var_names",
    )

    object_id: Optional[int]
    shader_var_names: Dict[str, str]
    view_matrix: Matrix4x4

    _position: np.ndarray
    _target: np.ndarray

    def __init__(
        self,
        target: Position3D = (0.0, 0.0, 0.0),
        position: Position3D = (0.0, 0.0, 0.0),
        **shader_var_names,
    ):
        """Initialize player view transformation"""
        self.object_id = None
        self.shader_var_names = shader_var_names

        self._position = np.array(position, dtype=np.float32)
        self._target = np.array(target, dtype=np.float32)

        self.recalculate_player_view()

    def increment_position(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """Increment the player's position by given amounts. Requires recalculate to update matrix."""
        if x:
            self._position[0] += x
        if y:
            self._position[1] += y
        if z:
            self._position[2] += z

    def set_position(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """Set the player's position to specific coordinates. Requires recalculate to update matrix."""
        if x:
            self._position[0] = x
        if y:
            self._position[1] = y
        if z:
            self._position[2] = z

    def set_target(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """Set the player's look target. Requires recalculate to update matrix."""
        if x:
            self._target[0] = x
        if y:
            self._target[1] = y
        if z:
            self._target[2] = z

    def recalculate_player_view(self):
        """
        Recalculate the player view matrix based on current parameters
        Atleast one of position, theta or phi must be set to True
        """
        self.view_matrix = matrix44.create_look_at(
            eye=self._position, target=self._target, up=[0.0, 1.0, 0.0]
        )

    def draw(self):
        """Update all player properties on the GPU"""
        glUniformMatrix4fv(self.object_id, 1, GL_FALSE, self.view_matrix)
