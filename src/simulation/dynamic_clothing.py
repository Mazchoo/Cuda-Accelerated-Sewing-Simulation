"""Class containing information to simulate clothing as one mesh"""

from typing import Dict, Optional

import numpy as np

from src.qt.gl_helpers.device_adapter import DeviceAllocationAdapter
from src.simulation.mesh import MeshData
from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.sewing_constraints import SewingConstraints

from src.simulation.setup.fuse_piece_relations import (
    get_piece_to_index_range_mapping,
    get_combined_vertex_data,
    get_combined_particle_relations,
    get_combined_sewing_relations,
    get_body_mesh_arrays,
)

from src.simulation.setup.cuda_variables import CudaVariables, CudaVariable
from src.simulation.apply_cuda_kernels import (
    apply_gravity,
    apply_stress,
    apply_shear,
    apply_bend,
    propagate_forces,
    apply_sewing,
    apply_collisions,
    recalculate_normals,
    copy_to_opengl_mesh_data,
)

from src.parameters import VELOCITY_DAMPING_START, VELOCITY_DAMPING_END, NR_STEPS


class DynamicClothing:
    """
    Manages physics of simulation
    Puts all pieces into a single array of positions
    """

    def __init__(
        self,
        pieces: Dict[str, DynamicPiece],
        sewing_constraints: SewingConstraints,
        body_mesh: MeshData,
    ):
        self.piece_to_index_range = get_piece_to_index_range_mapping(pieces)

        self.mesh = MeshData(
            get_combined_vertex_data(pieces, self.piece_to_index_range)
        )
        self.body_mesh = body_mesh
        body_triangles, body_centers, body_normals = get_body_mesh_arrays(
            body_mesh.trimesh
        )

        stress, shear, bend = get_combined_particle_relations(
            pieces, self.piece_to_index_range
        )

        sew_from_indices, sew_to_indices = get_combined_sewing_relations(
            sewing_constraints, self.piece_to_index_range
        )

        velocities = np.zeros((len(self.mesh), 3), dtype=np.float32)
        accelerations = np.zeros((len(self.mesh), 3), dtype=np.float32)

        self.cuda_variables = CudaVariables(
            vertices=CudaVariable(self.mesh.vertices_3d.copy()),
            normals=CudaVariable(self.mesh.normals.copy()),
            indices=CudaVariable(self.mesh.index_data.copy()),
            velocities=CudaVariable(velocities),
            accelerations=CudaVariable(accelerations),
            stress_indices=CudaVariable(stress),
            shear_indices=CudaVariable(shear),
            bend_indices=CudaVariable(bend),
            sewing_indices=CudaVariable(
                np.stack([sew_from_indices, sew_to_indices]).transpose()
            ),
            body_triangles=CudaVariable(body_triangles),
            body_triangle_centers=CudaVariable(body_centers),
            body_triangle_normals=CudaVariable(body_normals),
        )

    @property
    def vertices_3d(self) -> np.ndarray:
        """Get vertices on the gpu"""
        return self.cuda_variables.vertices.copy_from_gpu()

    def recalculate_dampening(self, step: int) -> np.float32:
        """Calculate dampening based on step"""
        if step > NR_STEPS:
            return np.float32(VELOCITY_DAMPING_END)

        dampening_cosine = 0.5 - 0.5 * np.cos(
            np.pi / NR_STEPS * step
        )  # Value between 0 and 1
        dampening = (
            VELOCITY_DAMPING_START
            + (VELOCITY_DAMPING_END - VELOCITY_DAMPING_START) * dampening_cosine
        )
        return np.float32(dampening)

    def update_forces(self, step: int, dampening: Optional[float] = None):
        """Update forces from internal interactions within piece"""
        if dampening is None:
            dampening: float = self.recalculate_dampening(step)

        apply_gravity(self.cuda_variables)
        apply_stress(self.cuda_variables)
        apply_shear(self.cuda_variables)
        apply_bend(self.cuda_variables)
        propagate_forces(self.cuda_variables, dampening)
        apply_sewing(self.cuda_variables)
        apply_collisions(self.cuda_variables)

    def copy_to_open_gl_data(self, open_gl_buffer: DeviceAllocationAdapter):
        """Copy cuda data on gpu from cuda context to open gl vertex buffer object"""
        recalculate_normals(self.cuda_variables)
        copy_to_opengl_mesh_data(self.cuda_variables, open_gl_buffer)
