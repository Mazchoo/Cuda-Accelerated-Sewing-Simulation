''' Container of all the information for an open GL draw call (outside the vertex and index data) '''
from OpenGL.GL import glEnable, glBlendFunc
from OpenGL.GL import GL_DEPTH_TEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA

from src.qt.gl_helpers.player import Player
from src.qt.gl_helpers.camera import Camera
from src.qt.gl_helpers.motion import Motion
from src.qt.gl_helpers.light import Light
from src.qt.gl_helpers.shader_program import ShaderProgram

from src.qt.shaders.shader_parameters import LIGHT_PROPERTIES
from src.parameters import (VERTEX_SHADER_PATH, FRAGMENT_SHADER_PATH,
                            MIN_CAMERA_DISTANCE_RATIO, DEFAULT_CAMERA_DISTANCE_RATIO,
                            MAX_CAMERA_DISTANCE_RATIO, FIELD_OF_VIEW,
                            LIGHT_POSITION_RATIO, LIGHT_COLOR,
                            LIGHT_REFLECTIVE_STRENGTH, LIGHT_AMBIENT_STRENGTH)


class DrawingPass:
    ''' Drawing pass data '''
    shader: ShaderProgram
    player: Player
    object_motion: Motion
    light: Light

    def __init__(self, height: float, aspect_ratio: float):
        self.shader = ShaderProgram(VERTEX_SHADER_PATH, FRAGMENT_SHADER_PATH)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        default_distance = DEFAULT_CAMERA_DISTANCE_RATIO * height
        min_distance = min(MIN_CAMERA_DISTANCE_RATIO * height, default_distance)
        max_distance = max(MAX_CAMERA_DISTANCE_RATIO * height, default_distance)

        camera = Camera(FIELD_OF_VIEW, aspect_ratio, min_distance, max_distance)

        # Viewing position is middle of body at default distance
        view_position = [0, height/2, -default_distance]
        self.player = Player(camera, position=view_position,
                             object_id="camera")
        self.player.bind_global_variable_names(self.shader)

        light_position = [0, LIGHT_POSITION_RATIO * height, 0]
        self.light = Light(light_position, LIGHT_COLOR,
                           LIGHT_REFLECTIVE_STRENGTH, LIGHT_AMBIENT_STRENGTH,
                           **LIGHT_PROPERTIES)
        self.light.bind_global_variable_names(self.shader)

        self.object_motion = Motion(object_id="motion")
        self.object_motion.bind_global_variable_names(self.shader)
