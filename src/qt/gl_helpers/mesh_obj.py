"""Drawable OpenGL mesh"""

from typing import Tuple, Dict, Optional
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

import pycuda.gl as cudagl

import src.simulation.apply_cuda_kernels  # noqa: F401
from src.simulation.mesh import MeshData
from src.qt.gl_helpers.material import Material
from src.qt.gl_helpers.shader_program import ShaderProgram
from src.qt.gl_helpers.material_parameters import MaterialParameters
from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable

from src.qt.shaders.shader_parameters import MATERIAL_PROPERTIES


class GLMesh(OpenGLUploadable):
    """Store vertex, indices and textures of an object and perform draw (set_all_globals)"""

    __slots__ = (
        "_vao",
        "_vbo",
        "_ebo",
        "material_iterator",
        "mesh_data",
        "_cuda_buffer_handle",
    )

    _vao: Optional[int]
    _vbo: int
    _ebo: int
    _cuda_buffer_handle: cudagl.RegisteredBuffer

    material_iterator: Tuple[Tuple[Material, int, int], ...]
    mesh_data: MeshData
    shader_var_names: Dict[str, str] = {}  # Empty

    def __init__(self, mesh_data: MeshData):
        self.mesh_data = mesh_data
        self._vao = None
        self._vbo = None
        self._ebo = None
        self._cuda_buffer_handle = None

        material_iterator = []
        for texture in self.mesh_data.texture_data:
            material_properties = MaterialParameters(texture["mtl"])

            texture_src = texture["mtl"]["texture"]
            material = Material(texture_src, material_properties, **MATERIAL_PROPERTIES)
            material_iterator.append((material, texture["count"], texture["offset"]))

        self.material_iterator = tuple(material_iterator)

    @property
    def cuda_buffer(self) -> Optional[cudagl.RegisteredBuffer]:
        """Return handle to vertex data"""
        return self._cuda_buffer_handle

    def _allocate_memory_buffers(self):
        """Delay allocation of vertex buffers as this can only be done in openGL context functions"""
        self._vao, self._vbo, self._ebo = self.generate_vertex_buffers(
            self.mesh_data.vertex_data, self.mesh_data.index_data.flatten()
        )
        self._cuda_buffer_handle = cudagl.RegisteredBuffer(
            int(self._vbo), cudagl.graphics_map_flags.WRITE_DISCARD
        )

    def generate_vertex_buffers(
        self, vertices: np.ndarray, indices: np.ndarray
    ) -> Tuple[int, int, int]:
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

    def draw(self):
        """Perform a drawing pass with all materials"""
        if self._vao is None:
            self._allocate_memory_buffers()

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)

        index_bytes = self.mesh_data.index_data.itemsize
        for material, count, offset in self.material_iterator:
            material.draw()
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

    def destroy(self):
        """Remove buffers after app is finished"""
        for material, _, _ in self.material_iterator:
            material.destroy()

        glDeleteVertexArrays(1, (self._vao,))
        glDeleteBuffers(1, (self._vbo, self._ebo))
