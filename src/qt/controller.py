"""Main controller module to create to do controller"""

from PyQt5.QtWidgets import QWidget

from src.qt.gl_helpers.common.window_helpers import set_window_icon
from src.qt.gl_helpers.common.controller_factory import CreateQtController


@CreateQtController  # initialise with window, model, layout
class SewingSimulationController(QWidget):
    """Sets up models, callbacks and UI for todo list implementation"""

    def __init__(self, *_args, **_kwargs):
        super().__init__()

    @staticmethod
    def setupCallbacks(controller):
        """Override add callbacks to layout of controller"""
        pass

    @staticmethod
    def initializeModels(controller):
        """Setup models"""
        pass

    @staticmethod
    def initializeUi(controller):
        """Override to set properties of ui components"""
        controller.parent.setWindowTitle(" Clothing Simulation")
        set_window_icon(controller.parent, "./assets/sewing_icon.png")
