import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QSurfaceFormat

from src.qt.gl_helpers.common.window_helpers import (
    load_qss,
    attach_qss_editor,
    edit_ui_template,
)

from src.qt.controller import SewingSimulationController
from src.qt.ui.SewingSimulationUI import Ui_MainWindow

if __name__ == "__main__":
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)

    parent_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(parent_window)
    ui = edit_ui_template(ui)
    widget = SewingSimulationController(
        parent_window, lambda *_args, **_kwargs: None, ui
    )

    if "RUN_QSS_EDITOR" in sys.argv:
        attach_qss_editor(parent_window)

    parent_window.show()

    load_qss(app, "src/qt/ui/SewingSimulation.qss")

    sys.exit(app.exec_())
