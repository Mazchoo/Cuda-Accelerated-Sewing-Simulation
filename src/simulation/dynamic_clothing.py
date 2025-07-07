""" Class containing information to simulate clothing as one mesh """
from typing import Dict

import numpy as np

from src.simulation.common import DistanceAdjustment
from src.simulation.mesh import MeshData
from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.sewing_constraints import SewingConstraints
from src.simulation.sewing_pair import SewingPairRelations
from src.simulation.setup.vertex_relationships import VertexRelations
from src.simulation.setup.fuse_piece_relations import (get_piece_to_index_range_mapping, get_combined_vertex_data,
                                                       get_combined_particle_relations, get_combined_sewing_relations,
                                                       get_body_mesh_arrays)

from src.simulation.setup.cuda_variables import CudaVariables, CudaVariable
from src.simulation.apply_cuda_kernels import apply_gravity


from src.parameters import (GRAVITY, VERTEX_RESOLUTION, TERMINAL_VELOCITY,
                            CM_PER_M, TIME_DELTA, STRESS_WEIGHTING, STRESS_THRESHOLD,
                            SHEAR_WEIGHTING, SHEAR_THRESHOLD,
                            BEND_WEIGHTING, BEND_THRESHOLD,
                            VELOCITY_DAMPING_START, VELOCITY_DAMPING_END, NR_STEPS)


class DynamicClothing:
    """
        Manages physics of simulation
        Puts all pieces into a single array of positions
    """
    def __init__(self, pieces: Dict[str, DynamicPiece],
                 sewing_constraints: SewingConstraints, body_mesh: MeshData):

        self.piece_to_index_range = get_piece_to_index_range_mapping(pieces)

        vertices, indices, textures = get_combined_vertex_data(pieces, self.piece_to_index_range)
        self.mesh = MeshData(vertices, indices, textures)
        self.body_mesh = body_mesh
        body_triangles, body_centers, body_normals = get_body_mesh_arrays(body_mesh.trimesh)

        stress, shear, bend = get_combined_particle_relations(pieces, self.piece_to_index_range)
        self.vertex_relations = VertexRelations(stress, shear, bend)

        sew_from_indices, sew_to_indices = get_combined_sewing_relations(sewing_constraints, self.piece_to_index_range)

        sewing_pair = SewingPairRelations('all', sew_from_indices, 'all', sew_to_indices)
        self.sewing_constraints = SewingConstraints([sewing_pair])

        self.velocities = np.zeros((len(self.mesh), 3), dtype=np.float32)
        self.accelerations = np.zeros((len(self.mesh), 3), dtype=np.float32)

        self.resting_straight_length = VERTEX_RESOLUTION / CM_PER_M
        self.resting_diagonal_length = np.sqrt(2) * VERTEX_RESOLUTION / CM_PER_M
        self.dampening_constant = np.pi / NR_STEPS

        self.cuda_varibales = CudaVariables(
            vertices=CudaVariable(vertices),
            velocities=CudaVariable(self.velocities),
            accelerations=CudaVariable(self.accelerations),
            stress_indices=CudaVariable(stress),
            shear_indices=CudaVariable(shear),
            bend_indices=CudaVariable(bend),
            sewing_indices=CudaVariable(np.stack([sew_from_indices, sew_to_indices]).transpose()),
            triangles=CudaVariable(body_triangles),
            triangle_centers=CudaVariable(body_centers),
            traingle_normals=CudaVariable(body_normals)
        )
        apply_gravity(self.cuda_varibales)

    @property
    def vertices_3d(self) -> np.ndarray:
        ''' Get vertices on the gpu '''
        return self.cuda_varibales.vertices.copy_from_gpu()

    def update_positions(self):
        """ Update positions from current velocities """
        self.mesh.offset_vertices(self.velocities * TIME_DELTA)
        self.mesh.clamp_above_zero()  # floor in y direction should always be positive

    def apply_dampening_to_velocity(self, step: int):
        """ Apply energy reductiont to the system depending on the step """
        dampening_cosine = 0.5 - 0.5 * np.cos(self.dampening_constant * step)  # Value between 0 and 1
        dampening = VELOCITY_DAMPING_START + (VELOCITY_DAMPING_END - VELOCITY_DAMPING_START) * dampening_cosine

        norms = np.linalg.norm(self.velocities, axis=1, keepdims=True)

        scales = np.minimum(1.0, TERMINAL_VELOCITY / norms) * dampening
        self.velocities *= scales

    def update_velocities(self, step: int):
        """ Update velocities from internal forces within piece """
        self.velocities += self.accelerations * TIME_DELTA
        self.apply_dampening_to_velocity(step)

    def apply_gravity(self):
        """ Apply downward gravity force """
        self.accelerations[:, 1] = -GRAVITY

    def apply_stress_force(self):
        """ Apply resistance to distrubance from resting length in horizontal and vertical direction """
        vertices = self.mesh.vertices_3d
        stress_relations = self.vertex_relations.stress_relations

        stress_vectors = (vertices[stress_relations[:, 1]] - vertices[stress_relations[:, 0]]) / self.resting_straight_length
        stress_distances = np.linalg.norm(stress_vectors, axis=1, keepdims=True)
        normed_stress = stress_vectors / np.where(stress_distances == 0, 1, stress_distances)
        stress_vectors -= normed_stress

        has_stress_compress_force = (stress_distances > 1 + STRESS_THRESHOLD).flatten()
        stress_compress_force_update = stress_vectors[has_stress_compress_force] * STRESS_WEIGHTING
        np.add.at(self.accelerations, stress_relations[has_stress_compress_force, 1], -stress_compress_force_update)
        np.add.at(self.accelerations, stress_relations[has_stress_compress_force, 0], stress_compress_force_update)

        has_stress_expand_force = (stress_distances < 1 - STRESS_THRESHOLD).flatten()
        expand_stress_force_update = stress_vectors[has_stress_expand_force] * STRESS_WEIGHTING
        np.add.at(self.accelerations, stress_relations[has_stress_expand_force, 1], expand_stress_force_update)
        np.add.at(self.accelerations, stress_relations[has_stress_expand_force, 0], -expand_stress_force_update)

    def apply_shear_force(self):
        """ Apply resistance to distrubance from resting length in diagonal directions """
        vertices = self.mesh.vertices_3d
        shear_relations = self.vertex_relations.shear_relations

        shear_vectors = (vertices[shear_relations[:, 1]] - vertices[shear_relations[:, 0]]) / self.resting_diagonal_length
        shear_distances = np.linalg.norm(shear_vectors, axis=1, keepdims=True)
        normed_shear = shear_vectors / np.where(shear_distances == 0, 1, shear_distances)
        shear_vectors -= normed_shear

        has_shear_compress_force = (shear_distances > 1 + SHEAR_THRESHOLD).flatten()
        shear_compress_force_update = shear_vectors[has_shear_compress_force] * SHEAR_WEIGHTING
        np.add.at(self.accelerations, shear_relations[has_shear_compress_force, 1], -shear_compress_force_update)
        np.add.at(self.accelerations, shear_relations[has_shear_compress_force, 0], shear_compress_force_update)

        has_shear_expand_force = (shear_distances < 1 - SHEAR_THRESHOLD).flatten()
        shear_shear_force_update = shear_vectors[has_shear_expand_force] * SHEAR_WEIGHTING
        np.add.at(self.accelerations, shear_relations[has_shear_expand_force, 1], shear_shear_force_update)
        np.add.at(self.accelerations, shear_relations[has_shear_expand_force, 0], -shear_shear_force_update)

    def apply_bend_force(self):
        """ Apply resistance to straight lines disturbed from rest """
        vertices = self.mesh.vertices_3d
        bend_relations = self.vertex_relations.bend_relations

        bend_start = vertices[bend_relations[:, 0]]
        bend_middle = vertices[bend_relations[:, 1]]
        bend_end = vertices[bend_relations[:, 2]]

        bend_direction = (bend_start + bend_end) * 0.5 - bend_middle
        bend_amount = np.linalg.norm(bend_direction, axis=1)
        has_bend_force = (bend_amount > BEND_THRESHOLD).flatten()

        bend_force_update = BEND_WEIGHTING * bend_direction[has_bend_force]
        np.add.at(self.accelerations, bend_relations[has_bend_force, 0], -bend_force_update * 0.5)
        np.add.at(self.accelerations, bend_relations[has_bend_force, 1], bend_force_update)
        np.add.at(self.accelerations, bend_relations[has_bend_force, 2], -bend_force_update * 0.5)

    def update_internal_forces(self):
        """ Update forces from internal interactions within piece """
        self.accelerations *= 0.
        self.apply_gravity()

        self.apply_stress_force()
        self.apply_shear_force()
        self.apply_bend_force()

    def body_collision_adjustment(self):
        """ Push vertices outside the body mesh """
        vertices = self.mesh.vertices_3d
        trimesh = self.body_mesh.trimesh

        is_inside_mesh = trimesh.contains(vertices)
        if not is_inside_mesh.any():
            return

        _, distances, triangle_ids = trimesh.nearest.on_surface(vertices[is_inside_mesh])
        adjustment = trimesh.face_normals[triangle_ids] * distances[:, np.newaxis]
        self.mesh.offset_vertices(adjustment, mask=is_inside_mesh)

    def apply_adjustment(self, adjustment: DistanceAdjustment):
        """ Apply a series of vertex adjustments to positions from external source """
        for inds, amount in adjustment:
            self.mesh.offset_vertices(amount, inds)
