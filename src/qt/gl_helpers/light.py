
import numpy as np
from OpenGL.GL import glUniform3fv, glUniform1f

from src.qt.gl_helpers.uniforms import bind_globals_to_object, get_global_object_id


class Light:
    def __init__(self, position: list, color: list, strength: float, **kwargs):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = float(strength)

        self.globals = kwargs
        self.position_glob_id = None
        self.color_glob_id = None
        self.strength_glob_id = None

    def set_position_to_global(self, shader: int = None, var_name: str = None):
        glob_id = get_global_object_id(self, "position_glob_id", shader, var_name)
        glUniform3fv(glob_id, 1, self.position)

    def set_color_to_global(self, shader: int = None, var_name: str = None):
        glob_id = get_global_object_id(self, "color_glob_id", shader, var_name)
        glUniform3fv(glob_id, 1, self.color)

    def set_strength_to_global(self, shader: int = None, var_name: str = None):
        glob_id = get_global_object_id(self, "strength_glob_id", shader, var_name)
        glUniform1f(glob_id, self.strength)

    def set_all_globals(self):
        self.set_position_to_global()
        self.set_color_to_global()
        self.set_strength_to_global()

    def bind_global_variable_names(self, shader):
        bind_globals_to_object(self, shader)
