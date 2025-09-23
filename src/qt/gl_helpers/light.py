"""Class to store and manage lighting properties for OpenGL rendering"""

from typing import Dict, Optional

import numpy as np
from OpenGL.GL import glUniform3fv, glUniform1f

from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable
from src.qt.gl_helpers.typing import ColorRGB, Position3D


class Light(OpenGLUploadable):
    """Stores the position, color, and strength of a light source"""

    _position: np.ndarray
    _color: np.ndarray
    _reflective_strength: float
    _ambient_strength: float

    shader_var_names: Dict[str, str]
    position_glob_id: Optional[int]
    color_glob_id: Optional[int]
    reflective_strength_glob_id: Optional[int]
    ambient_strength_glob_id: Optional[int]

    def __init__(
        self,
        position: Position3D,
        color: ColorRGB,
        reflective_strength: float,
        ambient_strength: float,
        **shader_var_names,
    ):
        self._position = np.array(position, dtype=np.float32)
        self._color = np.array(color, dtype=np.float32)
        self._reflective_strength = reflective_strength
        self._ambient_strength = ambient_strength

        self.shader_var_names = shader_var_names
        self.position_glob_id = None
        self.color_glob_id = None
        self.reflective_strength_glob_id = None
        self.ambient_strength_glob_id = None

    def set_position(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ):
        """Set the light's position to specific coordinates. Requires recalculate to a global update."""
        if x:
            self._position[0] = x
        if y:
            self._position[1] = y
        if z:
            self._position[2] = z

    def draw(self):
        """
        Update all light properties on the GPU
        Do not call from thread outside GL context
        """
        glUniform3fv(self.position_glob_id, 1, self._position)
        glUniform3fv(self.color_glob_id, 1, self._color)
        glUniform1f(self.reflective_strength_glob_id, self._reflective_strength)
        glUniform1f(self.ambient_strength_glob_id, self._ambient_strength)
