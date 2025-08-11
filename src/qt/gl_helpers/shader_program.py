""" OpenGL shader program management for loading and compiling vertex/fragment shaders """

from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import glUseProgram, glDeleteProgram, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER


class ShaderProgram:
    """ Manages OpenGL shader program lifecycle including compilation, usage, and cleanup """
    _id: int

    def __init__(self, vertex_file_path: str, fragment_file_path: str):
        """
            Load and compile vertex/fragment shaders from file paths.
            The compiled program is immediately activated
        """
        self._id = ShaderProgram._create_shader(vertex_file_path, fragment_file_path)
        glUseProgram(self._id)

    @property
    def gl_id(self) -> int:
        """ Returns the OpenGL program ID for direct access """
        return self._id

    def use(self):
        """ Activate this shader program for subsequent rendering operations """
        glUseProgram(self._id)

    def destroy(self):
        """ Clean up GPU resources by deleting the shader program """
        glDeleteProgram(self._id)

    @staticmethod
    def read_shader_file(path: str):
        """ Read shader source code from file and return as list of strings """
        with open(path, 'r') as f:
            source = f.readlines()
        return source

    @staticmethod
    def _create_shader(vertex_file_path: str, fragment_file_path: str) -> int:
        """ Compile vertex and fragment shaders into a complete shader program """
        vertex_source = ShaderProgram.read_shader_file(vertex_file_path)
        fragment_source = ShaderProgram.read_shader_file(fragment_file_path)

        return compileProgram(
            compileShader(vertex_source, GL_VERTEX_SHADER),
            compileShader(fragment_source, GL_FRAGMENT_SHADER)
        )
