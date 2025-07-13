''' Main controller module to create to do controller '''
from PyQt5.QtWidgets import QWidget

from src.qt.common.window_helpers import setWindowIcon
from src.qt.common.controller_factory import CreateQtController


@CreateQtController  # initialise with window, model, layout
class SewingSimulationController(QWidget):
    ''' Sets up models, callbacks and UI for todo list implementation '''

    def __init__(self, *_args, **_kwargs):
        super().__init__()

    @staticmethod
    def setupCallbacks(controller):
        ''' Override add callbacks to layout of controller '''
        pass

    @staticmethod
    def initializeModels(controller):
        ''' Setup models '''
        pass

    @staticmethod
    def initializeUi(controller):
        ''' Override to set properties of ui components '''
        controller.parent.setWindowTitle(" Clothing Simulation")
        setWindowIcon(controller.parent, './assets/sewing_icon.png')
