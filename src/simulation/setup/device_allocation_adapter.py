"""Workaround to provide a GPU address to cuda for OpenGL data"""

import pycuda.driver as cuda


class DeviceAllocationAdapter(cuda.PointerHolderBase):
    def __init__(self, ptr: int):
        self.gpudata = ptr

    def __int__(self):
        return self.gpudata
