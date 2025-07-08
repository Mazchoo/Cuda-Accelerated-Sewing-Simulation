''' Run cuda operations on cuda variables '''
import numpy as np

from src.parameters import DEFAULT_BLOCK_SIZE, COLLISION_BLOCK_SIZE
from src.simulation.setup.cuda_variables import CudaVariables
from src.simulation.setup.cuda_kernels import (GRAVITY_MODULE,
                                               STRESS_MODULE,
                                               SHEAR_MODULE,
                                               BEND_MODULE,
                                               UPDATE_POSITION_MODULE,
                                               SEWING_MODULE,
                                               COLLISION_MODULE)

DEFAULT_BLOCK_SHAPE = (DEFAULT_BLOCK_SIZE, 1, 1)
COLLISION_BLOCK_SHAPE = (COLLISION_BLOCK_SIZE, 1, 1)


def calculate_nr_blocks(num_ops: int, block_size: int) -> int:
    ''' Given number of operations and block size, find number of blocks needed '''
    return (num_ops + block_size - 1) // block_size


def apply_gravity(variables: CudaVariables):
    ''' Update accerlation in place for gravity '''
    accelerations = variables.accelerations
    nr_blocks = calculate_nr_blocks(len(accelerations), DEFAULT_BLOCK_SIZE)
    GRAVITY_MODULE(accelerations.gpu, accelerations.length,
                   block=DEFAULT_BLOCK_SHAPE, grid=(nr_blocks, 1, 1))


def apply_stress(variables: CudaVariables):
    ''' Update acceleration in place for stress '''
    nr_blocks = calculate_nr_blocks(len(variables.stress_indices), DEFAULT_BLOCK_SIZE)
    STRESS_MODULE(variables.accelerations.gpu,
                  variables.vertices.gpu,
                  variables.stress_indices.gpu,
                  variables.stress_indices.length,
                  block=DEFAULT_BLOCK_SHAPE,
                  grid=(nr_blocks, 1, 1))


def apply_shear(variables: CudaVariables):
    ''' Update acceleration in place for shear '''
    nr_blocks = calculate_nr_blocks(len(variables.shear_indices), DEFAULT_BLOCK_SIZE)
    SHEAR_MODULE(variables.accelerations.gpu,
                 variables.vertices.gpu,
                 variables.shear_indices.gpu,
                 variables.shear_indices.length,
                 block=DEFAULT_BLOCK_SHAPE,
                 grid=(nr_blocks, 1, 1))


def apply_bend(variables: CudaVariables):
    ''' Update acceleration in place for bend '''
    nr_blocks = calculate_nr_blocks(len(variables.bend_indices), DEFAULT_BLOCK_SIZE)
    BEND_MODULE(variables.accelerations.gpu,
                variables.vertices.gpu,
                variables.bend_indices.gpu,
                variables.bend_indices.length,
                block=DEFAULT_BLOCK_SHAPE,
                grid=(nr_blocks, 1, 1))


def apply_friction(variables: CudaVariables, dampening: np.float32):
    ''' Update position and velocity, taking friction into account '''
    nr_blocks = calculate_nr_blocks(len(variables.vertices), DEFAULT_BLOCK_SIZE)
    UPDATE_POSITION_MODULE(variables.accelerations.gpu,
                           variables.velocities.gpu,
                           variables.vertices.gpu,
                           variables.vertices.length,
                           dampening,
                           block=DEFAULT_BLOCK_SHAPE,
                           grid=(nr_blocks, 1, 1))


def apply_sewing(variables: CudaVariables):
    ''' Update positions for sewing constraints '''
    nr_blocks = calculate_nr_blocks(len(variables.sewing_indices), DEFAULT_BLOCK_SIZE)
    SEWING_MODULE(variables.vertices.gpu,
                  variables.sewing_indices.gpu,
                  variables.sewing_indices.length,
                  block=DEFAULT_BLOCK_SHAPE,
                  grid=(nr_blocks, 1, 1))


def apply_collisions(variables: CudaVariables):
    ''' Update positions to stop collision with body '''
    nr_blocks = calculate_nr_blocks(len(variables.vertices), COLLISION_BLOCK_SIZE)
    COLLISION_MODULE(variables.triangles.gpu,
                     variables.triangles.length,
                     variables.vertices.gpu,
                     variables.vertices.length,
                     variables.traingle_normals.gpu,
                     variables.triangle_centers.gpu,
                     block=COLLISION_BLOCK_SHAPE,
                     grid=(nr_blocks, 1, 1))
