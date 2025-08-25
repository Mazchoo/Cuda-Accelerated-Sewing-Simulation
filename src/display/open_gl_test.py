import sys
import numpy as np
import ctypes
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from OpenGL.GL import (
    glCreateProgram, glCreateShader, glShaderSource, glCompileShader,
    glAttachShader, glLinkProgram, glDeleteShader, glGenVertexArrays,
    glBindVertexArray, glGenBuffers, glBindBuffer, glBufferData,
    glVertexAttribPointer, glEnableVertexAttribArray, glEnable,
    glClearColor, glClear, glUseProgram, glGetUniformLocation,
    glUniformMatrix4fv, glDrawElements,
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_ARRAY_BUFFER, GL_STATIC_DRAW,
    GL_ELEMENT_ARRAY_BUFFER, GL_FLOAT, GL_FALSE, GL_DEPTH_TEST,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_TRIANGLES, GL_UNSIGNED_INT
)
from pyrr import matrix44, Vector3

VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 vColor;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    vColor = color;
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 vColor;
out vec4 fragColor;
void main()
{
    fragColor = vec4(vColor, 1.0);
}
"""


class GLWidget(QOpenGLWidget):
    def initializeGL(self):
        # Vertex data: positions and colors
        self.vertices = np.array([
            # positions        # colors
            -0.5, -0.5, 0.0,   1.0, 0.0, 0.0,  # Red
            0.5, -0.5, 0.0,   0.0, 1.0, 0.0,  # Green
            0.5,  0.5, 0.0,   0.0, 0.0, 1.0,  # Blue
            -0.5,  0.5, 0.0,   1.0, 1.0, 0.0   # Yellow
        ], dtype=np.float32)

        # EBO indices
        self.indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        # Compile shaders
        self.shader = glCreateProgram()
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, VERTEX_SHADER)
        glCompileShader(vs)
        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, FRAGMENT_SHADER)
        glCompileShader(fs)
        glAttachShader(self.shader, vs)
        glAttachShader(self.shader, fs)
        glLinkProgram(self.shader)
        glDeleteShader(vs)
        glDeleteShader(fs)

        # VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # EBO
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # color attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glEnable(GL_DEPTH_TEST)

    def paintGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader)

        # Matrices
        model = matrix44.create_identity(dtype=np.float32)
        view = matrix44.create_look_at(
            eye=Vector3([1.0, 1.0, 2.0]),
            target=Vector3([0.0, 0.0, 0.0]),
            up=Vector3([0.0, 1.0, 0.0]),
            dtype=np.float32
        )
        projection = matrix44.create_perspective_projection(
            fovy=45.0, aspect=self.width()/self.height(),
            near=0.1, far=10.0, dtype=np.float32
        )

        # Send uniforms
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GLWidget()
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec())
