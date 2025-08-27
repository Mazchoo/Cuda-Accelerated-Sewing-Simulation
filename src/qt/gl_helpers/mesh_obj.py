"""Drawable OpenGL mesh"""

from typing import Tuple, Dict
import ctypes

import numpy as np
from OpenGL.GL import (
    glBindVertexArray,
    glDrawElements,
    glDeleteVertexArrays,
    glDeleteBuffers,
    glGenVertexArrays,
    glGenBuffers,
    glBindBuffer,
    glBufferData,
    glBufferSubData,
    glEnableVertexAttribArray,
    glVertexAttribPointer,
)
from OpenGL.GL import (
    GL_TRIANGLES,
    GL_FLOAT,
    GL_ARRAY_BUFFER,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    GL_DYNAMIC_DRAW,
    GL_FALSE,
    GL_UNSIGNED_INT,
)

from src.simulation.mesh import MeshData
from src.qt.gl_helpers.material import Material
from src.qt.gl_helpers.shader_program import ShaderProgram
from src.qt.gl_helpers.material_parameters import MaterialParameters
from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable

from src.qt.shaders.shader_parameters import MATERIAL_PROPERTIES


class ObjMesh(OpenGLUploadable):
    """Store vertex, indices and textures of an object and perform draw (set_all_globals)"""

    __slots__ = "vao", "vbo", "ebo", "material_iterator", "mesh_data"

    vao: int
    vbo: int
    ebo: int
    material_iterator: Tuple[Tuple[Material, int, int], ...]
    mesh_data: MeshData
    globals: Dict[str, str] = {}  # Empty

    def __init__(self, mesh_data: MeshData):
        self.mesh_data = mesh_data

        self.vao, self.vbo, self.ebo = self.generate_vertex_buffers(
            self.mesh_data.vertex_data, self.mesh_data.index_data.flatten()
        )

        material_iterator = []
        for texture in self.mesh_data.texture_data:
            material_properties = MaterialParameters()
            material = Material(
                texture["path"], material_properties, **MATERIAL_PROPERTIES
            )
            material_iterator.append((material, texture["count"], texture["offset"]))

        self.material_iterator = tuple(material_iterator)

    def generate_vertex_buffers(self, vertices: np.ndarray, indices: np.ndarray):
        """Generate memory handles for vertex buffer"""
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vertices = np.asarray(vertices, dtype=np.float32, order="C")
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

        indices = np.asarray(indices, dtype=np.uint32, order="C")
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        self.layout_position_texture_normal()

        return vao, vbo, ebo

    def layout_position_texture_normal(self):
        """
        Instruct the latest vertex buffer object to read the data
        as x, y, z, s, t, nx, ny, nz
        (x, y, z) position
        (s, t) texture
        (nx, ny, nz) normal
        """
        comps_per_vertex = 8  # 3 pos + 2 uv + 3 norm
        stride = comps_per_vertex * ctypes.sizeof(
            ctypes.c_float
        )  # or vertices.itemsize * 8

        # positions: first 3 floats
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        # uvs: next 2 floats -> offset = 3 * sizeof(float)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1,
            2,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)),
        )

        # normals: next 3 floats -> offset = 5 * sizeof(float)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(
            2,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(5 * ctypes.sizeof(ctypes.c_float)),
        )

    def set_all_globals(self):
        """Perform a drawing pass with all materials"""
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        index_bytes = self.mesh_data.index_data.itemsize
        for material, count, offset in self.material_iterator:
            material.set_all_globals()
            glDrawElements(
                GL_TRIANGLES,
                count,
                GL_UNSIGNED_INT,
                ctypes.c_void_p(offset * index_bytes),
            )

    def bind_global_variable_names(self, shader: ShaderProgram):
        """(Override) Bind all the materials to a shader, this object has special handling for re-uploading vertices"""
        for material, _, _ in self.material_iterator:
            material.bind_global_variable_names(shader)

    def reupload_vertices(self):
        """Reupload vertex data to the GPU"""
        vertices = self.mesh_data.vertex_data
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)

    def destroy(self):
        """Remove buffers after app is finished"""
        for material, _, _ in self.material_iterator:
            material.destroy()

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo, self.ebo))
