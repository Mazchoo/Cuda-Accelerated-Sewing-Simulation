"""Main controller module to create to do controller"""

from PyQt5.QtWidgets import QWidget

from src.qt.common.window_helpers import set_window_icon
from src.qt.common.controller_factory import CreateQtController

from src.qt.mouse_drag import MouseDrag
from src.qt.actions import open_body_mesh, open_clothing_json
from src.qt.events import handle_wheel_event


@CreateQtController  # initialise with window, model, layout
class SewingSimulationController(QWidget):
    """Sets up models, callbacks and UI for todo list implementation"""

    def __init__(self, *_args, **_kwargs):
        super().__init__()

    @staticmethod
    def setupCallbacks(controller):
        """Override add callbacks to layout of controller"""
        controller.layout.actionOpen_Body.triggered.connect(
            lambda _: open_body_mesh(controller)
        )
        controller.layout.actionOpen_Clothing.triggered.connect(
            lambda _: open_clothing_json(controller)
        )
        # Install wheel event handler on the OpenGL widget
        controller.layout.openGLWidget.wheelEvent = lambda event: handle_wheel_event(
            event, controller
        )

        controller.layout.openGLWidget.mousePressEvent = MouseDrag.mouse_press_handler
        controller.layout.openGLWidget.mouseReleaseEvent = MouseDrag.mouse_release_handler

    @staticmethod
    def initializeModels(_controller):
        """Setup models"""
        return

    @staticmethod
    def initializeUi(controller):
        """Override to set properties of ui components"""
        controller.parent.setWindowTitle(" Clothing Simulation")
        set_window_icon(controller.parent, "./assets/sewing_icon.png")
