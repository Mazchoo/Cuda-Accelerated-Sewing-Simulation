''' Container of all the information for an open GL draw call (outside the vertex and index data) '''
from typing import NamedTuple

from src.qt.player import Player
from src.qt.camera import Camera
from src.qt.motion import Motion
from src.qt.light import Light
from src.qt.shader_program import ShaderProgram

from src.parameters import (MIN_CAMERA_DISTANCE_RATIO, DEFAULT_CAMERA_DISTANCE_RATIO,
                            MAX_CAMERA_DISTANCE_RATIO, FIELD_OF_VIEW)


class DrawingPass(NamedTuple):
    ''' Drawing pass data '''
    player: Player
    object_motion: Motion
    light: Light
    shader: ShaderProgram

    def __init__(self, height: float, aspect_ratio: float):
        default_distance = DEFAULT_CAMERA_DISTANCE_RATIO * height
        min_distance = min(MIN_CAMERA_DISTANCE_RATIO * height, default_distance)
        max_distance = max(MAX_CAMERA_DISTANCE_RATIO * height, default_distance)
        camera = Camera(FIELD_OF_VIEW, aspect_ratio, min_distance, max_distance)
