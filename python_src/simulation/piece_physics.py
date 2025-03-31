""" Class containing information to simulate a dynamic clothing mesh """
import numpy as np

from python_src.simulation.mesh import MeshData
from python_src.simulation.vertex_relationships import VertexRelations

from python_src.parameters import (GRAVITY, VERTEX_RESOLUTION, MAX_VELOCITY,
                                   TIME_DELTA, STRESS_WEIGHTING, STRESS_THRESHOLD)


class DynamicPiece:
    """ Simulated with physics helpers """
    def __init__(self, mesh: MeshData, vertex_relations: VertexRelations):
        self.mesh = mesh
        self.vertex_relations = vertex_relations

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
        vertices = self.mesh.vertices_3d
        stress_relations = self.vertex_relations.stress_relations

        stress_vectors = vertices[stress_relations[:, 1]] - vertices[stress_relations[:, 0]]
        stress_distances = np.linalg.norm(stress_vectors, axis=1) / self.resting_straight_length

        has_compress_force = stress_distances > 1 + STRESS_THRESHOLD
        self.acceleration[stress_relations[:, 1][has_compress_force]] += stress_vectors * STRESS_WEIGHTING
        self.acceleration[stress_relations[:, 0][has_compress_force]] -= stress_vectors * STRESS_WEIGHTING

        has_expand_force = stress_distances < 1 - STRESS_THRESHOLD
        self.acceleration[stress_relations[:, 1][has_expand_force]] -= stress_vectors * STRESS_WEIGHTING
        self.acceleration[stress_relations[:, 0][has_expand_force]] += stress_vectors * STRESS_WEIGHTING
