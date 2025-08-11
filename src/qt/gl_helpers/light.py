''' Class to store and manage lighting properties for OpenGL rendering '''
from typing import Dict, Optional

import numpy as np
from OpenGL.GL import glUniform3fv, glUniform1f

from src.qt.gl_helpers.uniforms import bind_globals_to_object, get_global_object_id
from src.qt.gl_helpers.typing import ColorRGB, Position3D


class Light:
    ''' Stores the position, color, and strength of a light source '''

    position: np.ndarray
    color: np.ndarray
    strength: float
    globals: Dict[str, str]
    position_glob_id: Optional[int]
    color_glob_id: Optional[int]
    strength_glob_id: Optional[int]

    def __init__(self, position: Position3D,
                 color: ColorRGB, strength: float, **globals):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = float(strength)

        self.globals = globals
        self.position_glob_id = None
        self.color_glob_id = None
        self.strength_glob_id = None

    def set_position_to_global(self, shader: int = None, var_name: str = None):
        ''' Copy light position to GPU uniform variable '''
        glob_id = get_global_object_id(self, "position_glob_id", shader, var_name)
        glUniform3fv(glob_id, 1, self.position)

    def set_color_to_global(self, shader: int = None, var_name: str = None):
        ''' Copy light color to GPU uniform variable '''
        glob_id = get_global_object_id(self, "color_glob_id", shader, var_name)
        glUniform3fv(glob_id, 1, self.color)

    def set_strength_to_global(self, shader: int = None, var_name: str = None):
        ''' Copy light strength to GPU uniform variable '''
        glob_id = get_global_object_id(self, "strength_glob_id", shader, var_name)
        glUniform1f(glob_id, self.strength)

    def set_all_globals(self):
        ''' Update all light properties on the GPU '''
        self.set_position_to_global()
        self.set_color_to_global()
        self.set_strength_to_global()

    def bind_global_variable_names(self, shader):
        ''' Bind light properties to uniform variable names in the shader '''
        bind_globals_to_object(self, shader)
