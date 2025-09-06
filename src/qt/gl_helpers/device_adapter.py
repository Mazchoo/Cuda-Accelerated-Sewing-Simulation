"""Helper class to provide valid input to cuda kernels from OpenGL data"""

import pycuda.driver as cuda


class DeviceAllocationAdapter(cuda.PointerHolderBase):
    """Adapter the immitates the memory address to cuda allocated memory"""

    def __init__(self, ptr):
        self.gpudata = ptr

    def __int__(self):
        return self.gpudata
