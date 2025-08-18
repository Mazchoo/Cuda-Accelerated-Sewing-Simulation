''' Helper functions for interacting with uniform variables on GPU from OpenGL '''
from abc import ABC, abstractmethod
from typing import Dict

from OpenGL.GL import glGetUniformLocation

from src.qt.gl_helpers.shader_program import ShaderProgram


class OpenGLUploadable(ABC):
    globals: Dict[str, str]

    def bind_global_variable_names(self, shader: ShaderProgram):
        ''' For an object that implements GL container upload all variables to GPU '''
        shader.use()
        for var_name, global_name in self.globals.items():
            global_uniform = glGetUniformLocation(shader.gl_id, global_name)
            setattr(self, var_name, global_uniform)
        self.set_all_globals()

    def assert_all_globals_are_set(self):
        """Run a check that all globals are set"""
        assert isinstance(getattr(self, 'globals'), dict)
        for key in self.globals.keys():
            assert getattr(self, key) is not None

    @abstractmethod
    def set_all_globals(self):
        pass
