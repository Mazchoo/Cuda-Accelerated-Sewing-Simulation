''' Class to store and manage lighting properties for OpenGL rendering '''
from typing import Dict, Optional

import numpy as np
from OpenGL.GL import glUniform3fv, glUniform1f

from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable
from src.qt.gl_helpers.typing import ColorRGB, Position3D


class Light(OpenGLUploadable):
    ''' Stores the position, color, and strength of a light source '''

    position: np.ndarray
    color: np.ndarray
    reflective_strength: float
    ambient_strength: float

    globals: Dict[str, str]
    position_glob_id: Optional[int]
    color_glob_id: Optional[int]
    reflective_strength_glob_id: Optional[int]
    ambient_strength_glob_id: Optional[int]

    def __init__(self, position: Position3D, color: ColorRGB,
                 reflective_strength: float, ambient_strength: float, **globals):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.reflective_strength = reflective_strength
        self.ambient_strength = ambient_strength

        self.globals = globals
        self.position_glob_id = None
        self.color_glob_id = None
        self.reflective_strength_glob_id = None
        self.ambient_strength_glob_id = None

    def set_position_to_global(self):
        ''' Copy light position to GPU uniform variable '''
        glUniform3fv(self.position_glob_id, 1, self.position)

    def set_color_to_global(self):
        ''' Copy light color to GPU uniform variable '''
        glUniform3fv(self.color_glob_id, 1, self.color)

    def set_strength_to_global(self):
        ''' Copy light strength to GPU uniform variable '''
        glUniform1f(self.strength_glob_id, self.reflective_strength)

    def set_all_globals(self):
        ''' Update all light properties on the GPU '''
        self.set_position_to_global()
        self.set_color_to_global()
        self.set_strength_to_global()
