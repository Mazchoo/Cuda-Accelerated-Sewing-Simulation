import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from src.qt.common.window_helpers import load_qss, attach_qss_editor, edit_ui_template

from src.qt.controller import SewingSimulationController
from UI.SewingSimulationUI import Ui_MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    parent_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(parent_window)
    layout = edit_ui_template(ui)
    widget = SewingSimulationController(parent_window, lambda *_args, **_kwargs: None, layout)

    if 'RUN_QSS_EDITOR' in sys.argv:
        attach_qss_editor(parent_window)

    parent_window.show()

    load_qss(app, "UI/SewingSimulation.qss")

    sys.exit(app.exec_())
