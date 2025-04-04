""" Class containing information to simulate a dynamic clothing mesh """
import numpy as np

from python_src.simulation.mesh import MeshData
from python_src.simulation.vertex_relationships import VertexRelations

from python_src.parameters import (GRAVITY, VERTEX_RESOLUTION, MAX_VELOCITY, CM_PER_M,
                                   TIME_DELTA, STRESS_WEIGHTING, STRESS_THRESHOLD,
                                   SHEAR_WEIGHTING, SHEAR_THRESHOLD)


class DynamicPiece:
    """ Simulated with physics helpers """
    def __init__(self, mesh: MeshData, vertex_relations: VertexRelations):
        self.mesh = mesh
        self.vertex_relations = vertex_relations

        self.velocity = np.zeros((self.mesh.nr_vertices, 3), dtype=np.float32)
        self.acceleration = np.zeros((self.mesh.nr_vertices, 3), dtype=np.float32)
        self.acceleration[:, 1] = -GRAVITY

        self.resting_straight_length = VERTEX_RESOLUTION / CM_PER_M
        self.resting_diagonal_length = np.sqrt(2) * VERTEX_RESOLUTION / CM_PER_M

    def update_positions(self):
        """ Update positions from current velocities """
        self.mesh.offset_vertices(self.velocity * TIME_DELTA)
        self.mesh.clamp_above_zero()

    def update_velocities(self):
        """ Update velocities from internal forces within piece """
        self.velocity += self.acceleration * TIME_DELTA
        norms = np.linalg.norm(self.velocity, axis=1, keepdims=True)
        scales = np.minimum(1.0, MAX_VELOCITY / norms)
        self.velocity *= scales

    def update_forces(self):
        """ Update forces from internal interactions within piece """
        vertices = self.mesh.vertices_3d
        self.acceleration *= 0.
        self.acceleration[:, 1] = -GRAVITY

        stress_relations = self.vertex_relations.stress_relations

        stress_vectors = (vertices[stress_relations[:, 1]] - vertices[stress_relations[:, 0]]) / self.resting_straight_length
        stress_distances = np.linalg.norm(stress_vectors, axis=1, keepdims=True)
        normed_stress = stress_vectors / np.where(stress_distances == 0, 1, stress_distances)
        stress_vectors -= normed_stress

        has_stress_compress_force = (stress_distances > 1 + STRESS_THRESHOLD).flatten()
        stress_compress_force_update = stress_vectors[has_stress_compress_force] * STRESS_WEIGHTING
        np.add.at(self.acceleration, stress_relations[has_stress_compress_force, 1], -stress_compress_force_update)
        np.add.at(self.acceleration, stress_relations[has_stress_compress_force, 0], stress_compress_force_update)

        has_stress_expand_force = (stress_distances < 1 - STRESS_THRESHOLD).flatten()
        expand_stress_force_update = stress_vectors[has_stress_expand_force] * STRESS_WEIGHTING
        np.add.at(self.acceleration, stress_relations[has_stress_expand_force, 1], expand_stress_force_update)
        np.add.at(self.acceleration, stress_relations[has_stress_expand_force, 0], -expand_stress_force_update)

        shear_relations = self.vertex_relations.shear_relations

        shear_vectors = (vertices[shear_relations[:, 1]] - vertices[shear_relations[:, 0]]) / self.resting_diagonal_length
        shear_distances = np.linalg.norm(shear_vectors, axis=1, keepdims=True)
        normed_shear = shear_vectors / np.where(shear_distances == 0, 1, shear_distances)
        shear_vectors -= normed_shear

        has_shear_compress_force = (shear_distances > 1 + SHEAR_THRESHOLD).flatten()
        shear_compress_force_update = shear_vectors[has_shear_compress_force] * SHEAR_WEIGHTING
        np.add.at(self.acceleration, shear_relations[has_shear_compress_force, 1], -shear_compress_force_update)
        np.add.at(self.acceleration, shear_relations[has_shear_compress_force, 0], shear_compress_force_update)

        has_shear_expand_force = (shear_distances < 1 - SHEAR_THRESHOLD).flatten()
        shear_shear_force_update = shear_vectors[has_shear_expand_force] * SHEAR_WEIGHTING
        np.add.at(self.acceleration, shear_relations[has_shear_expand_force, 1], shear_shear_force_update)
        np.add.at(self.acceleration, shear_relations[has_shear_expand_force, 0], -shear_shear_force_update)
