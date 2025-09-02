"""Highest level of implementations of actions"""

from typing import Self
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog


def open_body_mesh(controller: Self):
    """Adds a body mesh to the simulation (tries to find annotations as well)"""
    file_dialog = QFileDialog()
    file_dialog.setNameFilter("OBJ files (*.obj)")
    file_dialog.setWindowTitle("Open Body Mesh")
    file_dialog.setFileMode(QFileDialog.ExistingFile)

    if file_dialog.exec_():
        selected_files = file_dialog.selectedFiles()
        if not selected_files:
            return
        body_path = Path(selected_files[0])

        if not body_path.exists() and body_path.suffix != ".obj":
            print("File provided is not an .obj file")
            return

        annotations_path = body_path.parent / f"{body_path.stem}.json"
        if not annotations_path.exists():
            print("Annotation file not accompanying the .obj file")
            return

        controller.layout.openGLWidget.add_body(str(body_path), str(annotations_path))
