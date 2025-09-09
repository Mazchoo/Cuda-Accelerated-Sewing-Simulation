"""Container of all the information for an open GL draw call (outside the vertex and index data)"""

from typing import Optional, ContextManager

import OpenGL.GL as gl

from src.qt.gl_helpers.player import Player
from src.qt.gl_helpers.camera import Camera
from src.qt.gl_helpers.motion import Motion
from src.qt.gl_helpers.light import Light
from src.qt.gl_helpers.shader_program import ShaderProgram
from src.qt.gl_helpers.mesh_obj import GLMesh

from src.qt.gl_helpers.device_adapter import DeviceAllocationAdapter
from src.qt.gl_helpers.copy_to_gl_context import gl_context_vertex_data

from src.simulation.mesh import MeshData
from src.qt.shaders.shader_parameters import LIGHT_PROPERTIES
from src.parameters import (
    VERTEX_SHADER_PATH,
    FRAGMENT_SHADER_PATH,
    MIN_CAMERA_DISTANCE_RATIO,
    DEFAULT_CAMERA_DISTANCE_RATIO,
    MAX_CAMERA_DISTANCE_RATIO,
    FIELD_OF_VIEW,
    LIGHT_POSITION_RATIO,
    LIGHT_COLOR,
    LIGHT_REFLECTIVE_STRENGTH,
    LIGHT_AMBIENT_STRENGTH,
    CLOTHING_Z_FACTOR,
    CLOTHING_Z_OFFSET,
)


class DrawingPass:
    """Drawing pass data"""

    shader: ShaderProgram
    camera: Camera
    player: Player
    object_motion: Motion
    light: Light
    body_mesh: Optional[GLMesh]
    clothing_mesh: Optional[GLMesh]

    def __init__(self, aspect_ratio: float):
        self.shader = ShaderProgram(VERTEX_SHADER_PATH, FRAGMENT_SHADER_PATH)

        default_distance = DEFAULT_CAMERA_DISTANCE_RATIO
        min_distance = min(MIN_CAMERA_DISTANCE_RATIO, default_distance)
        max_distance = max(MAX_CAMERA_DISTANCE_RATIO, default_distance)

        self.camera = Camera(
            FIELD_OF_VIEW, aspect_ratio, min_distance, max_distance, object_id="camera"
        )
        self.camera.bind_global_variable_names(self.shader)

        # Viewing position is middle of body at default distance
        view_position = [0, 0.5, default_distance]
        view_target = [0, 0.5, 0]
        self.player = Player(
            position=view_position, target=view_target, object_id="projection"
        )
        self.player.bind_global_variable_names(self.shader)

        light_position = [0, LIGHT_POSITION_RATIO, 0]
        self.light = Light(
            light_position,
            LIGHT_COLOR,
            LIGHT_REFLECTIVE_STRENGTH,
            LIGHT_AMBIENT_STRENGTH,
            **LIGHT_PROPERTIES,
        )
        self.light.bind_global_variable_names(self.shader)

        self.object_motion = Motion(object_id="motion")
        self.object_motion.bind_global_variable_names(self.shader)

        self.body_mesh = None
        self.clothing_mesh = None

    def update_body_height(self, height: float):
        """Set the camera and light to a default position based on body height"""
        self.shader.use()
        default_distance = DEFAULT_CAMERA_DISTANCE_RATIO * height
        min_distance = min(MIN_CAMERA_DISTANCE_RATIO * height, default_distance)
        max_distance = max(MAX_CAMERA_DISTANCE_RATIO * height, default_distance)

        self.camera.recalculate_projection(near=min_distance, far=max_distance)
        self.camera.draw()

        self.player.set_position(0.0, height / 2, default_distance)
        self.player.set_target(0.0, height / 2, 0.0)
        self.player.recalculate_player_view()
        self.player.draw()

        self.light.set_position(0.0, LIGHT_POSITION_RATIO * height, 0)
        self.light.draw()

    def add_body_mesh(self, mesh: MeshData):
        """Add a body mesh to the simulation"""
        self.shader.use()
        self.body_mesh = GLMesh(mesh)
        self.body_mesh.bind_global_variable_names(self.shader)

    def add_clothing_mesh(self, mesh: MeshData):
        """Add a clothing mesh to the simulation"""
        self.shader.use()
        self.clothing_mesh = GLMesh(mesh)
        self.clothing_mesh.bind_global_variable_names(self.shader)

    def edit_clothing_vertex_data_context(
        self,
    ) -> ContextManager[Optional[DeviceAllocationAdapter]]:
        """Return context mananger"""
        return gl_context_vertex_data(self.clothing_mesh.cuda_buffer)

    def update_aspect_ratio(self, aspect_ratio: float):
        """Update the aspect ratio of the camera"""
        self.shader.use()
        self.camera.recalculate_projection(aspect=aspect_ratio)
        self.camera.draw()

    def draw(self):
        """Perform a drawing pass"""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.shader.use()
        if self.body_mesh:
            self.body_mesh.draw()
        if self.clothing_mesh:
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
            gl.glPolygonOffset(CLOTHING_Z_FACTOR, CLOTHING_Z_OFFSET)
            self.clothing_mesh.draw()
            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL)
