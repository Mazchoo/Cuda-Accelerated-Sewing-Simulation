"""Workaround to provide a GPU address to cuda for OpenGL data"""

import pycuda.driver as cuda


class DeviceAllocationAdapter(cuda.PointerHolderBase):  # pylint: disable=no-member
    """Allows pointer to be used to upload to CUDA"""

    def __init__(self, ptr: int):
        self.gpudata = ptr

    def __int__(self):
        return self.gpudata
