''' Operations that change the properties of Qt windows '''
import os

try:
    from pyqss import Qss as QssEditor
except ImportError:
    print("Warning: pyqss not installed")

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMainWindow

CWD = os.getcwd()
QSS_CACHE = {}


def loadQss(component: QWidget, file_name: str):
    ''' Replace the qss of a component '''
    path = f"{CWD}/{file_name}"

    if path not in QSS_CACHE:
        with open(path, 'r', encoding='utf-8') as f:
            QSS_CACHE[path] = f.read()

    component.setStyleSheet(QSS_CACHE[path])


def setWindowIcon(widget: QMainWindow, file_name: str):
    ''' Set the icon of a window loaded from a file '''
    icon = QIcon(f"{CWD}/{file_name}")
    widget.setWindowIcon(icon)


def attachQssEditor(widget: QWidget):
    ''' Create qss editor and attach it to current window '''
    qss_editor = QssEditor(widget)
    qss_editor.show()
