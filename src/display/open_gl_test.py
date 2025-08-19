import sys
import ctypes
import numpy as np
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from OpenGL.GL import *


VERT_SHADER_SRC = """
#version 330 core
layout (location = 0) in vec3 aPos;

void main()
{
    gl_Position = vec4(aPos, 1.0);
}
"""

FRAG_SHADER_SRC = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0, 0.2, 0.3, 1.0); // flat red/pink
}
"""


def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader


def create_program():
    vs = compile_shader(VERT_SHADER_SRC, GL_VERTEX_SHADER)
    fs = compile_shader(FRAG_SHADER_SRC, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    if not glGetProgramiv(prog, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(prog).decode())
    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog


class GLTest(QOpenGLWidget):
    def initializeGL(self):
        # Compile and link program
        self.program = create_program()

        # Vertex data: 3 vertices, positions only
        vertices = np.array([
            [ 0.0,  0.5, 0.0],
            [ 0.5, -0.5, 0.0],
            [-0.5, -0.5, 0.0],
        ], dtype=np.float32)

        indices = np.array([0, 1, 2], dtype=np.uint32)

        # Generate VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # EBO
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Vertex attrib pointer
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, ctypes.c_void_p(0))

        # Unbind (optional safety)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GLTest()
    w.resize(600, 600)
    w.show()
    sys.exit(app.exec_())
