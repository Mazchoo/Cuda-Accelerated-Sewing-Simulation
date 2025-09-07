"""Run cuda operations on cuda variables"""

import numpy as np

from src.simulation.setup.cuda_variables import CudaVariables
from src.simulation.setup.device_allocation_adapter import DeviceAllocationAdapter
from src.simulation.setup.cuda_kernels import (
    GRAVITY_KERNEL,
    STRESS_KERNEL,
    SHEAR_KERNEL,
    BEND_KERNEL,
    UPDATE_POSITION_KERNEL,
    SEWING_KERNEL,
    COLLISION_KERNEL,
    ZERO_OUT_NORMALS_KERNEL,
    SUM_TRIANGLE_NORMALS_KERNEL,
    NORMALIZE_NORMALS_KERNEL,
    COPY_TO_VERTEX_DATA_KERNEL,
)

from src.parameters import DEFAULT_BLOCK_SIZE, COLLISION_BLOCK_SIZE

DEFAULT_BLOCK_SHAPE = (DEFAULT_BLOCK_SIZE, 1, 1)
COLLISION_BLOCK_SHAPE = (COLLISION_BLOCK_SIZE, 1, 1)


def calculate_nr_blocks(num_ops: int, block_size: int) -> int:
    """Given number of operations and block size, find number of blocks needed"""
    return (num_ops + block_size - 1) // block_size


def apply_gravity(variables: CudaVariables):
    """Update accerlation in place for gravity"""
    accelerations = variables.accelerations
    nr_blocks = calculate_nr_blocks(len(accelerations), DEFAULT_BLOCK_SIZE)
    GRAVITY_KERNEL(
        accelerations.gpu,
        accelerations.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def apply_stress(variables: CudaVariables):
    """Update acceleration in place for stress"""
    nr_blocks = calculate_nr_blocks(len(variables.stress_indices), DEFAULT_BLOCK_SIZE)
    STRESS_KERNEL(
        variables.accelerations.gpu,
        variables.vertices.gpu,
        variables.stress_indices.gpu,
        variables.stress_indices.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def apply_shear(variables: CudaVariables):
    """Update acceleration in place for shear"""
    nr_blocks = calculate_nr_blocks(len(variables.shear_indices), DEFAULT_BLOCK_SIZE)
    SHEAR_KERNEL(
        variables.accelerations.gpu,
        variables.vertices.gpu,
        variables.shear_indices.gpu,
        variables.shear_indices.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def apply_bend(variables: CudaVariables):
    """Update acceleration in place for bend"""
    nr_blocks = calculate_nr_blocks(len(variables.bend_indices), DEFAULT_BLOCK_SIZE)
    BEND_KERNEL(
        variables.accelerations.gpu,
        variables.vertices.gpu,
        variables.bend_indices.gpu,
        variables.bend_indices.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def apply_friction(variables: CudaVariables, dampening: np.float32):
    """Update position and velocity, taking friction into account"""
    nr_blocks = calculate_nr_blocks(len(variables.vertices), DEFAULT_BLOCK_SIZE)
    UPDATE_POSITION_KERNEL(
        variables.accelerations.gpu,
        variables.velocities.gpu,
        variables.vertices.gpu,
        variables.vertices.gpu_length,
        dampening,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def apply_sewing(variables: CudaVariables):
    """Update positions for sewing constraints"""
    nr_blocks = calculate_nr_blocks(len(variables.sewing_indices), DEFAULT_BLOCK_SIZE)
    SEWING_KERNEL(
        variables.vertices.gpu,
        variables.sewing_indices.gpu,
        variables.sewing_indices.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def apply_collisions(variables: CudaVariables):
    """Update positions to stop collision with body"""
    nr_blocks = calculate_nr_blocks(len(variables.vertices), COLLISION_BLOCK_SIZE)
    COLLISION_KERNEL(
        variables.body_triangles.gpu,
        variables.body_triangles.gpu_length,
        variables.vertices.gpu,
        variables.vertices.gpu_length,
        variables.body_triangle_normals.gpu,
        variables.body_triangle_centers.gpu,
        block=COLLISION_BLOCK_SHAPE,
        grid=(nr_blocks, 1, 1),
    )


def recalculate_normals(variables: CudaVariables):
    """Recalculate normals for each vertex"""
    normals_nr_blocks = calculate_nr_blocks(len(variables.normals), DEFAULT_BLOCK_SIZE)
    indices_nr_blocks = calculate_nr_blocks(len(variables.indices), DEFAULT_BLOCK_SIZE)

    ZERO_OUT_NORMALS_KERNEL(
        variables.normals.gpu,
        variables.normals.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(normals_nr_blocks, 1, 1),
    )
    SUM_TRIANGLE_NORMALS_KERNEL(
        variables.normals.gpu,
        variables.vertices.gpu,
        variables.indices.gpu,
        variables.indices.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(indices_nr_blocks, 1, 1),
    )
    NORMALIZE_NORMALS_KERNEL(
        variables.normals.gpu,
        variables.normals.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(normals_nr_blocks, 1, 1),
    )


def copy_to_opengl_mesh_data(
    variables: CudaVariables, open_gl_buffer: DeviceAllocationAdapter
):
    """Copy cuda data to gpu"""
    vertices_nr_blocks = calculate_nr_blocks(len(variables.normals), DEFAULT_BLOCK_SIZE)

    COPY_TO_VERTEX_DATA_KERNEL(
        open_gl_buffer,
        variables.vertices.gpu,
        variables.normals.gpu,
        variables.vertices.gpu_length,
        block=DEFAULT_BLOCK_SHAPE,
        grid=(vertices_nr_blocks, 1, 1),
    )
