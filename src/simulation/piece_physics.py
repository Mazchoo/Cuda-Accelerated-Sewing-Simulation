""" Class containing information to simulate a dynamic clothing mesh """
import numpy as np
from trimesh import Trimesh

from src.simulation.common import DistanceAdjustment
from src.simulation.mesh import MeshData
from src.simulation.setup.vertex_relationships import VertexRelations

from src.parameters import (GRAVITY, VERTEX_RESOLUTION, MAX_TENSILE_VELOCITY,
                            CM_PER_M, TIME_DELTA, STRESS_WEIGHTING, STRESS_THRESHOLD,
                            SHEAR_WEIGHTING, SHEAR_THRESHOLD, FRICTION_CONSTANT,
                            BEND_WEIGHTING, BEND_THRESHOLD,
                            VELOCITY_DAMPING_START, VELOCITY_DAMPING_END, NR_STEPS)


class DynamicPiece:
    """ Simulated with physics helpers """
    def __init__(self, mesh: MeshData, vertex_relations: VertexRelations,
                 snap_point_name: str, alignment_point_name: str):
        self.mesh = mesh
        self.vertex_relations = vertex_relations

        self.velocity = np.zeros((self.mesh.nr_vertices, 3), dtype=np.float32)
        self.acceleration = np.zeros((self.mesh.nr_vertices, 3), dtype=np.float32)
        self.acceleration[:, 1] = -GRAVITY

        self.resting_straight_length = VERTEX_RESOLUTION / CM_PER_M
        self.resting_diagonal_length = np.sqrt(2) * VERTEX_RESOLUTION / CM_PER_M
        self.dampening_constant = np.pi / NR_STEPS

        self._snap_point_name = snap_point_name
        self._alignment_point_name = alignment_point_name

    @property
    def snap_point(self) -> np.ndarray:
        """ Return point to snap to body by offset """
        return self.mesh.get_annotation(self._snap_point_name)

    @property
    def snap_point_name(self) -> str:
        """ Get name of point to snap to on body by offset """
        return self._snap_point_name

    @property
    def alignment_point(self) -> np.ndarray:
        """ Return point to rotate other point to so matches orientation of body
            i.e. snap to alignment vector on piece matches snap to alignment on body """
        return self.mesh.get_annotation(self._alignment_point_name)

    @property
    def alignment_point_name(self) -> str:
        """ Get name of alignment point """
        return self._alignment_point_name

    @property
    def align_vector(self) -> np.ndarray:
        """ Get alignment vector from snap-point to alignment point """
        return self.alignment_point - self.snap_point

    def update_positions(self):
        """ Update positions from current velocities """
        self.mesh.offset_vertices(self.velocity * TIME_DELTA)
        self.mesh.clamp_above_zero()  # floor in y direction should always be positive

    def apply_dampening_to_velocity(self, step: int):
        """ Apply energy reductiont to the system depending on the step """
        norms = np.linalg.norm(self.velocity, axis=1, keepdims=True)
        dampening_cosine = 0.5 - 0.5 * np.cos(self.dampening_constant * step)  # Value between 0 and 1
        dampening = VELOCITY_DAMPING_START + (VELOCITY_DAMPING_END - VELOCITY_DAMPING_START) * dampening_cosine

        scales = np.minimum(1.0, MAX_TENSILE_VELOCITY / norms) * dampening
        self.velocity *= scales

    def update_velocities(self, step: int):
        """ Update velocities from internal forces within piece """
        self.velocity += self.acceleration * TIME_DELTA
        self.apply_dampening_to_velocity(step)

    def apply_gravity(self):
        """ Apply downward gravity force """
        self.acceleration[:, 1] = -GRAVITY

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
        np.add.at(self.acceleration, stress_relations[has_stress_compress_force, 1], -stress_compress_force_update)
        np.add.at(self.acceleration, stress_relations[has_stress_compress_force, 0], stress_compress_force_update)

        has_stress_expand_force = (stress_distances < 1 - STRESS_THRESHOLD).flatten()
        expand_stress_force_update = stress_vectors[has_stress_expand_force] * STRESS_WEIGHTING
        np.add.at(self.acceleration, stress_relations[has_stress_expand_force, 1], expand_stress_force_update)
        np.add.at(self.acceleration, stress_relations[has_stress_expand_force, 0], -expand_stress_force_update)

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
        np.add.at(self.acceleration, shear_relations[has_shear_compress_force, 1], -shear_compress_force_update)
        np.add.at(self.acceleration, shear_relations[has_shear_compress_force, 0], shear_compress_force_update)

        has_shear_expand_force = (shear_distances < 1 - SHEAR_THRESHOLD).flatten()
        shear_shear_force_update = shear_vectors[has_shear_expand_force] * SHEAR_WEIGHTING
        np.add.at(self.acceleration, shear_relations[has_shear_expand_force, 1], shear_shear_force_update)
        np.add.at(self.acceleration, shear_relations[has_shear_expand_force, 0], -shear_shear_force_update)

    def apply_friction(self):
        """ Apply friction in the oposite direction of velocity """
        self.acceleration -= FRICTION_CONSTANT * self.velocity

    def apply_bend_forces(self):
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
        np.add.at(self.acceleration, bend_relations[has_bend_force, 0], -bend_force_update * 0.5)
        np.add.at(self.acceleration, bend_relations[has_bend_force, 1], bend_force_update)
        np.add.at(self.acceleration, bend_relations[has_bend_force, 2], -bend_force_update * 0.5)

    def update_internal_forces(self):
        """ Update forces from internal interactions within piece """
        self.acceleration *= 0.
        self.apply_gravity()

        self.apply_stress_force()
        self.apply_shear_force()
        self.apply_bend_forces()
        self.apply_friction()

    def body_collision_adjustment(self, body_trimesh: Trimesh):
        """ Push vertices outside the body mesh """
        vertices = self.mesh.vertices_3d

        is_inside_mesh = body_trimesh.contains(vertices)
        if not is_inside_mesh.any():
            return

        _, distances, triangle_ids = body_trimesh.nearest.on_surface(vertices[is_inside_mesh])
        adjustment = body_trimesh.face_normals[triangle_ids] * distances[:, np.newaxis]
        self.mesh.offset_vertices(adjustment, mask=is_inside_mesh)

    def apply_adjustment(self, adjustment: DistanceAdjustment):
        """ Apply a series of vertex adjustments to positions from external source """
        for inds, amount in adjustment:
            self.mesh.offset_vertices(amount, inds)
