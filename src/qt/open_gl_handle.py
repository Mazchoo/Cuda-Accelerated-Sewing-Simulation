''' Functions to handle open gl operations on canvas '''
import OpenGL.GL as gl

from PyQt5.QtWidgets import QOpenGLWidget


class SewingGLWidget(QOpenGLWidget):
    def initializeGL(self):
        gl.glClearColor(0.2, 0.3, 0.4, 1.0)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
