"""Context manager to safely copy from a cuda context to open GL vertex data"""

from typing import Optional
from contextlib import contextmanager

import pycuda.gl as cudagl

from src.qt.gl_helpers.device_adapter import DeviceAllocationAdapter


@contextmanager
def gl_context_vertex_data(registered_buffer: Optional[cudagl.RegisteredBuffer]):
    """Create context of access to open gl memory buffer"""
    try:
        if registered_buffer is None:
            yield None
        else:
            mapping = registered_buffer.map()
            ptr, _ = mapping.device_ptr_and_size()

            yield DeviceAllocationAdapter(ptr)
    finally:
        if registered_buffer is not None:
            mapping.unmap()
