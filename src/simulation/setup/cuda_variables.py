"""Container for all cuda arrays"""

from typing import NamedTuple

import pycuda.driver as cuda
import numpy as np


class CudaVariable:
    """Correspondence between cpu and gpu variable"""

    def __init__(self, arr: np.ndarray):
        self.cpu = arr
        self.gpu = cuda.mem_alloc(arr.nbytes)
        cuda.memcpy_htod(self.gpu, arr.flatten())
        self.gpu_length = np.uint32(len(arr))

    def copy_from_gpu(self) -> np.ndarray:
        """Get updated variable from GPU"""
        cuda.memcpy_dtoh(self.cpu, self.gpu)
        return self.cpu

    def __len__(self) -> int:
        return int(self.gpu_length)


class CudaVariables(NamedTuple):
    """Container for cpu and gpu versions of each variable"""

    vertices: CudaVariable
    normals: CudaVariable
    indices: CudaVariable
    velocities: CudaVariable
    accelerations: CudaVariable
    stress_indices: CudaVariable
    shear_indices: CudaVariable
    bend_indices: CudaVariable
    sewing_indices: CudaVariable
    body_triangles: CudaVariable
    body_triangle_centers: CudaVariable
    body_triangle_normals: CudaVariable
