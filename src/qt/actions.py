"""Highest level of implementations of actions"""

from typing import TYPE_CHECKING
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog

from src.qt.open_gl_handle import SewingGLWidget
from src.utils.read_obj import parse_obj, read_json
from src.simulation.simulation import FabricSimulation
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices

from src.parameters import AVATAR_SCALING

if TYPE_CHECKING:
    from src.qt.controller import SewingSimulationController


def open_body_mesh(controller: "SewingSimulationController"):
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

        if not body_path.exists() or body_path.suffix != ".obj":
            print("File provided is not an .obj file")
            return

        annotations_path = body_path.parent / f"{body_path.stem}.json"
        if not annotations_path.exists():
            print("Annotation file not accompanying the .obj file")
            return

        try:
            avatar_mesh = parse_obj(str(body_path), str(annotations_path))
        except FileNotFoundError:
            print(f"Could not read file {body_path} annotations {annotations_path}")
            return

        avatar_mesh.scale_vertices(AVATAR_SCALING)

        controller.layout.openGLWidget.add_body(avatar_mesh)
        controller.layout.actionOpen_Clothing.setEnabled(True)


def open_clothing_json(controller: "SewingSimulationController"):
    """Opens a file dialog to select a JSON file for clothing."""
    file_dialog = QFileDialog()
    file_dialog.setNameFilter("JSON files (*.json)")
    file_dialog.setWindowTitle("Open Clothing JSON")
    file_dialog.setFileMode(QFileDialog.ExistingFile)

    if file_dialog.exec_():
        selected_files = file_dialog.selectedFiles()
        if not selected_files:
            return
        clothing_json_path = Path(selected_files[0])

        if not clothing_json_path.exists() or clothing_json_path.suffix != ".json":
            print("File provided is not a .json file")
            return

        open_gl_handle: SewingGLWidget = controller.layout.openGLWidget
        if not (body_mesh := open_gl_handle.drawing_pass.body_mesh):
            print("Avatar is not already present")
            return

        body_mesh_data = body_mesh.mesh_data
        clothing_data = read_json("./assets/sewing_shirt.json")
        all_pieces, sewing_constraints = extract_all_piece_vertices(
            clothing_data, body_mesh_data
        )

        open_gl_handle.fabric_simulation = FabricSimulation(
            body_mesh_data, all_pieces, sewing_constraints
        )
        open_gl_handle.add_clothing(open_gl_handle.fabric_simulation.clothing.mesh)
