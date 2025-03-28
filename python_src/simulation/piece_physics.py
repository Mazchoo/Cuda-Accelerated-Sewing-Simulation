""" Class containing information to simulate a dynamic clothing mesh """
import numpy as np

from python_src.simulation.mesh import MeshData
from python_src.simulation.vertex_relationships import VertexRelations

from python_src.parameters import GRAVITY, VERTEX_RESOLUTION, MAX_VELOCITY, TIME_DELTA


class DynamicPiece:
    """ Simulated with physics helpers """
    def __init__(self, mesh: MeshData, vertex_realtions: VertexRelations):
        self.mesh = mesh
        self.vertex_realtions = vertex_realtions

        self.velocity = np.zeros((self.mesh.nr_vertices, 3), dtype=np.float32)
        self.acceleration = np.zeros((self.mesh.nr_vertices, 3), dtype=np.float32)
        self.acceleration[:, 1] = -GRAVITY

        self.resting_straight_length = VERTEX_RESOLUTION
        self.resting_diagonal_length = np.sqrt(2) * VERTEX_RESOLUTION

    def update_positions(self):
        """ Update positions from current velocities """
        self.mesh.offset_vertices(self.velocity * TIME_DELTA)

    def update_velocities(self):
        """ Update velocities from internal forces within piece """
        self.velocity += self.acceleration * TIME_DELTA
        norms = np.linalg.norm(self.velocity, axis=1, keepdims=True)
        scales = np.minimum(1.0, MAX_VELOCITY / norms)
        self.velocity *= scales

    def update_forces(self):
        """ Update forces from internal interactions within piece """
        pass
