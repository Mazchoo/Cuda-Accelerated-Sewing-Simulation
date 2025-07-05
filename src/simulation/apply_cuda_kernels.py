''' Run cuda operations on cuda variables '''
import numpy.typing as npt

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
    return (int(num_ops) + int(block_size) - 1) // int(block_size)


def apply_gravity(variables: CudaVariables):
    ''' Update accerlation in place for gravity '''
    accelerations = variables.accelerations
    nr_blocks = calculate_nr_blocks(len(accelerations))
    GRAVITY_MODULE(accelerations.gpu, len(accelerations),
                   block=DEFAULT_BLOCK_SHAPE, grid=(nr_blocks, 1, 1))


def apply_stress(variables: CudaVariables):
    ''' Update acceleration in place for stress '''
    nr_blocks = calculate_nr_blocks(len(variables.stress_indices))
    STRESS_MODULE(variables.accelerations.gpu,
                  variables.vertices.gpu,
                  variables.stress_indices.gpu,
                  len(variables.stress_indices),
                  block=DEFAULT_BLOCK_SHAPE,
                  grid=(nr_blocks, 1, 1))


def apply_shear(variables: CudaVariables):
    ''' Update acceleration in place for shear '''
    nr_blocks = calculate_nr_blocks(len(variables.shear_indices))
    SHEAR_MODULE(variables.accelerations.gpu,
                 variables.vertices.gpu,
                 variables.shear_indices.gpu,
                 len(variables.shear_indices),
                 block=DEFAULT_BLOCK_SHAPE,
                 grid=(nr_blocks, 1, 1))


def apply_bend(variables: CudaVariables):
    ''' Update acceleration in place for bend '''
    nr_blocks = calculate_nr_blocks(len(variables.bend_indices))
    BEND_MODULE(variables.accelerations.gpu,
                variables.vertices.gpu,
                variables.bend_indices.gpu,
                len(variables.bend_indices),
                block=DEFAULT_BLOCK_SHAPE,
                grid=(nr_blocks, 1, 1))


def apply_friction(variables: CudaVariables, dampening: npt.float32):
    ''' Update position and velocity, taking friction into account '''
    nr_blocks = calculate_nr_blocks(len(variables.vertices))
    UPDATE_POSITION_MODULE(variables.accelerations.gp,
                           variables.velocities.gp,
                           variables.vertices.gpu,
                           len(variables.vertices),
                           dampening,
                           block=DEFAULT_BLOCK_SHAPE,
                           grid=(nr_blocks, 1, 1))


def apply_sewing(variables: CudaVariables):
    ''' Update positions for sewing constraints '''
    nr_blocks = calculate_nr_blocks(len(variables.sewing_indices))
    SEWING_MODULE(variables.vertices.gpu,
                  variables.sewing_indices.gpu,
                  len(variables.sewing_indices),
                  block=DEFAULT_BLOCK_SHAPE,
                  grid=(nr_blocks, 1, 1))


def apply_collisions(variables: CudaVariables):
    ''' Update positions to stop collision with body '''
    nr_blocks = calculate_nr_blocks(len(variables.vertices))
    COLLISION_MODULE(variables.triangles.gpu,
                     len(variables.triangles),
                     variables.vertices.gpu,
                     len(variables.vertices),
                     variables.traingle_normals.gpu,
                     variables.triangle_centers.gpu,
                     block=COLLISION_BLOCK_SHAPE,
                     grid=(nr_blocks, 1, 1))
