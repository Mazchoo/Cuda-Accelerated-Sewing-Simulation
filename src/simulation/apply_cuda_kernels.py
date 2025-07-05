''' Run cuda operations on cuda variables '''
from src.parameters import DEFAULT_BLOCK_SIZE, RAY_TRACING_BLOCK_SIZE
from src.simulation.setup.cuda_kernels import (GRAVITY_MODULE,
                                               STRESS_MODULE,
                                               SHEAR_MODULE)
from src.simulation.setup.cuda_variables import CudaVariables

DEFAULT_BLOCK_SHAPE = (DEFAULT_BLOCK_SIZE, 1, 1)
RAY_TRACE_BLOCK_SHAPE = (RAY_TRACING_BLOCK_SIZE, 1, 1)


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
    ''' Update acceleration in place for stress '''
    nr_blocks = calculate_nr_blocks(len(variables.shear_indices))
    SHEAR_MODULE(variables.accelerations.gpu,
                 variables.vertices.gpu,
                 variables.shear_indices.gpu,
                 len(variables.shear_indices),
                 block=DEFAULT_BLOCK_SHAPE,
                 grid=(nr_blocks, 1, 1))
