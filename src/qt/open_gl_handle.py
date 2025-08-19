''' Functions to handle open gl operations on canvas '''
from typing import Optional

import OpenGL.GL as gl

from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow

from src.utils.read_obj import parse_obj
from src.qt.gl_helpers.drawing import DrawingPass

from src.parameters import BODY_PATH, BODY_ANNOTATIONS_PATH, AVATAR_SCALING


class SewingGLWidget(QOpenGLWidget):
    ''' Creates rendering loop for sewing simulation '''
    drawing_pass: Optional[DrawingPass]

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.drawing_pass = None

    def initializeGL(self):
        ''' Qt Callback for initial setup '''
        print("GL version:", gl.glGetString(gl.GL_VERSION).decode())
        print("GLSL version:", gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode())
        print("Vendor:", gl.glGetString(gl.GL_VENDOR).decode())

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(0.2, 0.3, 0.4, 1.0)

        avatar_mesh = parse_obj(BODY_PATH, BODY_ANNOTATIONS_PATH)
        avatar_mesh.scale_vertices(AVATAR_SCALING)

        w, h = 1346, 907  # ToDo - make this dynamic

        self.drawing_pass = DrawingPass(w / h, avatar_mesh)

    def paintGL(self):
        ''' Qt Callback for updating on every frame '''
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.drawing_pass.draw()

    def resizeGL(self, w, h):
        ''' Qt Callback for updating viewport '''
        gl.glViewport(0, 0, w, h)
