import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from src.qt.common.window_helpers import loadQss, attachQssEditor

from src.qt.controller import SewingSimulationController
from UI.SewingSimulationUI import Ui_MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    parent_window = QMainWindow()
    widget = SewingSimulationController(parent_window, lambda *_args, **_kwargs: None, Ui_MainWindow)

    if 'RUN_QSS_EDITOR' in sys.argv:
        attachQssEditor(parent_window)

    parent_window.show()

    loadQss(app, "UI/SewingSimulation.qss")

    sys.exit(app.exec_())
