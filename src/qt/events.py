"""Handle the different events that the GUI can trigger"""

from typing import TYPE_CHECKING

from PyQt5.QtGui import QWheelEvent

if TYPE_CHECKING:
    from src.qt.controller import SewingSimulationController
    from src.qt.gl_helpers.drawing import DrawingPass


MOUSE_ACCELERATION = 1 / 1200


def handle_wheel_event(event: QWheelEvent, controller: "SewingSimulationController"):
    """Handle mouse wheel scroll events and print scroll amount"""
    if drawing_pass := controller.layout.openGLWidget.drawing_pass:
        drawing_pass: "DrawingPass"
        if drawing_pass.body_mesh:
            delta = event.angleDelta().y() * MOUSE_ACCELERATION
            drawing_pass.player.increment_position(z=delta)
            drawing_pass.player.recalculate_player_view()
            drawing_pass.redraw_player = True

    event.accept()
