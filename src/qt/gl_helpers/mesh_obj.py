'''  '''
from types import Iterable, Tuple
import ctypes

import numpy as np
from OpenGL.GL import (glBindVertexArray, glDrawArrays,
                       glDeleteVertexArrays, glDeleteBuffers,
                       glGenVertexArrays, glGenBuffers,
                       glBindBuffer, glBufferData,
                       glEnableVertexAttribArray, glVertexAttribPointer)
from OpenGL.GL import (GL_TRIANGLES, GL_FLOAT, GL_ARRAY_BUFFER,
                       GL_STATIC_DRAW, GL_FALSE)

from src.simulation.mesh import MeshData
from src.qt.gl_helpers.material import Material
from src.qt.gl_helpers.shader_program import ShaderProgram
from src.qt.gl_helpers.material_parameters import MaterialParameters
from src.qt.gl_helpers.uniforms import bind_globals_to_object


class ObjMesh:

    __slots__ = 'vao', 'vbo', 'material_iterator', 'mesh_data'

    vao: int
    vbo: int
    material_iterator: Iterable[Tuple[Material, int, int]]
    mesh_data: MeshData

    def __init__(self, mesh_data: MeshData):

        self.mesh_data = mesh_data

        self.vao, self.vbo = self.generate_vertex_buffers(self.mesh_data.vertex_data)

        draw_iterator = []
        for key, texture in self.mesh_data.texture_data.items():
            material_properties = MaterialParameters()
            material = Material(key, material_properties)
            draw_iterator.append((material, texture['count'], texture['offset']))

        self.draw_iterator = tuple(self.draw_iterator)

    def generate_vertex_buffers(self, vertices: np.ndarray):
        ''' Generate memory handles for vertex buffer '''
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        self.layout_position_texture_normal()

    def layout_position_texture_normal(self):
        '''
            Instruct the latest vertex buffer object to read the data
            as x, y, z, s, t, nx, ny, nz
            (x, y, z) position
            (s, t) texture
            (nx, ny, nz) normal
        '''
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def draw(self):
        """ Perform a drawing pass with all materials """
        glBindVertexArray(self.vao)

        for material, count, offset in self.draw_iterator:
            material.set_all_globals()
            glDrawArrays(GL_TRIANGLES, offset, count)

    def bind_global_variable_names(self, shader: ShaderProgram):
        ''' Bind player properties to uniform variable names in the shader, sets current state to global '''
        shader.use()
        bind_globals_to_object(self, shader.gl_id)
        self.set_all_globals()

    def destroy(self):
        """ Remove buffers after app is finished """
        for material, _, _ in self.draw_iterator:
            material.destroy()

        glDeleteVertexArrays(1, (self.vao, ))
        glDeleteBuffers(1, (self.vbo, ))
