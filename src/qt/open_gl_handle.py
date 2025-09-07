"""Functions to handle open gl operations on canvas"""

from typing import Optional

import OpenGL.GL as gl

from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow

from src.simulation.mesh import MeshData
from src.simulation.simulation import FabricSimulation
from src.qt.gl_helpers.drawing import DrawingPass

from src.parameters import STEPS_PER_FRAME


class SewingGLWidget(QOpenGLWidget):
    """
    Creates rendering loop for sewing simulation
    The vertex data of rendered objects can only be used in the GL functions
    The GL functions run on their own thread
    """

    drawing_pass: Optional[DrawingPass]
    fabric_simulation: Optional[FabricSimulation]
    frame_count: int
    end_frame: float

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.drawing_pass = None
        self.fabric_simulation = None
        self.frame_count = 0

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

    def add_body(self, body_mesh: MeshData):
        """Append body mesh to rendering"""
        self.drawing_pass.update_body_height(body_mesh.height)
        self.drawing_pass.add_body_mesh(body_mesh)

    def add_clothing(self, mesh: MeshData):
        """Append clothing mesh to rendering"""
        self.drawing_pass.add_clothing_mesh(mesh)

    def draw(self):
        """Draw a frame"""
        self.drawing_pass.draw()

    def paintGL(self):
        """Qt Callback for updating on every frame"""
        if self.fabric_simulation is not None:
            self.fabric_simulation.step(self.frame_count)

            if self.frame_count % STEPS_PER_FRAME == 0:
                self.draw()

                with self.drawing_pass.edit_clothing_vertex_data_context() as buffer:
                    if buffer is not None:
                        self.fabric_simulation.write_vertex_data_to_gl_buffer(buffer)

            self.frame_count += 1
        else:
            self.draw()

        self.update()

    def resizeGL(self, w: int, h: int):
        """Qt Callback for updating viewport"""
        gl.glViewport(0, 0, w, h)
        self.drawing_pass.update_aspect_ratio(w / h)
