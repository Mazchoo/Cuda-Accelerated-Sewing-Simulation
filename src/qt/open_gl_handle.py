''' Functions to handle open gl operations on canvas '''
import OpenGL.GL as gl

from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow


class SewingGLWidget(QOpenGLWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)

        self.meshes = []

    def initializeGL(self):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(0.2, 0.3, 0.4, 1.0)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
