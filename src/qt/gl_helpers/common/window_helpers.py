"""Operations that change the properties of Qt windows"""

import os

try:
    from pyqss import Qss as QssEditor
except ImportError:
    print("Warning: pyqss not installed")

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMainWindow

from src.qt.ui.SewingSimulationUI import Ui_MainWindow
from src.qt.open_gl_handle import SewingGLWidget


CWD = os.getcwd()
QSS_CACHE = {}


def load_qss(component: QWidget, file_name: str):
    """Replace the qss of a component"""
    path = f"{CWD}/{file_name}"

    if path not in QSS_CACHE:
        with open(path, "r", encoding="utf-8") as f:
            QSS_CACHE[path] = f.read()

    component.setStyleSheet(QSS_CACHE[path])


def set_window_icon(widget: QMainWindow, file_name: str):
    """Set the icon of a window loaded from a file"""
    icon = QIcon(f"{CWD}/{file_name}")
    widget.setWindowIcon(icon)


def attach_qss_editor(widget: QWidget):
    """Create qss editor and attach it to current window"""
    qss_editor = QssEditor(widget)
    qss_editor.show()


def edit_ui_template(ui: Ui_MainWindow) -> Ui_MainWindow:
    """Call back to change properties of UI to custom components"""

    # Replace the placeholder with your custom OpenGL widget
    layout = ui.openGLWidget.parent().layout()
    idx = layout.indexOf(ui.openGLWidget)

    # Remove the old widget
    layout.removeWidget(ui.openGLWidget)
    ui.openGLWidget.setParent(None)

    # Insert your subclassed widget in the same place
    ui.openGLWidget = SewingGLWidget(ui.mainGroupBox.parent().parent())
    layout.insertWidget(idx, ui.openGLWidget)
    return ui
