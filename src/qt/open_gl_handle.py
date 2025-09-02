"""Functions to handle open gl operations on canvas"""

from typing import Optional

import OpenGL.GL as gl

from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow

from src.simulation.mesh import MeshData
from src.utils.read_obj import parse_obj
from src.qt.gl_helpers.drawing import DrawingPass

from src.parameters import AVATAR_SCALING


class SewingGLWidget(QOpenGLWidget):
    """Creates rendering loop for sewing simulation"""

    drawing_pass: Optional[DrawingPass]

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.drawing_pass = None

    def initializeGL(self):
        """Qt Callback for initial setup"""
        print("GL version:", gl.glGetString(gl.GL_VERSION).decode())
        print("GLSL version:", gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode())
        print("Renderer:", gl.glGetString(gl.GL_RENDERER).decode())
        print("Vendor:", gl.glGetString(gl.GL_VENDOR).decode())

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(0.2, 0.3, 0.4, 1.0)

        w, h = self.width(), self.height()  # ToDo - make this dynamic
        self.drawing_pass = DrawingPass(w / h)

    def add_body(self, body_path: str, annotations_path: str):
        """Append body mesh to rendering"""
        avatar_mesh = parse_obj(body_path, annotations_path)
        avatar_mesh.scale_vertices(AVATAR_SCALING)

        self.drawing_pass.update_body_height(avatar_mesh.height)
        self.drawing_pass.add_mesh(avatar_mesh)

    def add_clothing(self, mesh: MeshData):
        """Append clothing mesh to rendering"""
        self.drawing_pass.add_mesh(mesh)

    def paintGL(self):
        """Qt Callback for updating on every frame"""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.drawing_pass.draw()

    def resizeGL(self, w, h):
        """Qt Callback for updating viewport"""
        gl.glViewport(0, 0, w, h)
        self.drawing_pass.update_aspect_ratio(w / h)
