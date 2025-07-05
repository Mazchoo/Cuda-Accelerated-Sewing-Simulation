''' All compiled cuda kernels '''

import pycuda.autoinit  # noqa
from pycuda.compiler import SourceModule
import numpy as np

from profiling.common import read_file_str, replace_constants_in_kernel

from parameters import (GRAVITY, VERTEX_RESOLUTION, CM_PER_M,
                        STRESS_THRESHOLD, STRESS_WEIGHTING,
                        SHEAR_THRESHOLD, SHEAR_WEIGHTING,
                        BEND_THRESHOLD, BEND_WEIGHTING,
                        TIME_DELTA, TERMINAL_VELOCITY,
                        SEWING_ADJUSTMENT_STEP)

# Update acceleration with gravity
GRAVITY_MODULE = SourceModule(
    replace_constants_in_kernel(
        read_file_str('./profiling/kernels/apply_gravity.cu'), {
            "GRAVITY": GRAVITY
        })
).get_function("apply_gravity")

# Apply stress relationships to apply force on particles
STRESS_MODULE = SourceModule(
    replace_constants_in_kernel(
        read_file_str('./profiling/kernels/apply_stress.cu'), {
            "STRESS_THRESHOLD": STRESS_THRESHOLD,
            "STRESS_WEIGHTING": STRESS_WEIGHTING,
            "STRESS_RESTING_AMOUNT": VERTEX_RESOLUTION / CM_PER_M
        })
).get_function("apply_stress")

# Apply shear relationships to apply force on particles
SHEAR_MODULE = SourceModule(
    replace_constants_in_kernel(
        read_file_str('./profiling/kernels/apply_stress.cu'), {
            "STRESS_THRESHOLD": SHEAR_THRESHOLD,
            "STRESS_WEIGHTING": SHEAR_WEIGHTING,
            "STRESS_RESTING_AMOUNT": (VERTEX_RESOLUTION * np.sqrt(2)) / CM_PER_M
        })
).get_function("apply_stress")

# Apply bend relationships to apply force on particles
BEND_MODULE = SourceModule(
    replace_constants_in_kernel(
        read_file_str('./profiling/kernels/apply_bend.cu'), {
            "BEND_THRESHOLD": BEND_THRESHOLD,
            "BEND_WEIGHTING": BEND_WEIGHTING
        })
).get_function("apply_bend")

# Update velocity, apply friction and then update position
UPDATE_POSITION_MODULE = SourceModule(
    replace_constants_in_kernel(
        read_file_str('./profiling/kernels/update_position.cu'), {
            "TIME_DELTA": TIME_DELTA,
            "TERMINAL_VELOCITY": TERMINAL_VELOCITY
        })
).get_function("update_position_with_friction")

# Apply sewing constraints
SEWING_MODULE = SourceModule(
    replace_constants_in_kernel(
        read_file_str('./profiling/kernels/apply_sewing_constraints.cu'), {
            "TIME_DELTA": TIME_DELTA,
            "SEWING_MAX_ADJUSTMENT": SEWING_ADJUSTMENT_STEP
        })
).get_function("apply_sewing_constraints")

# Move points to go outside the body
RAY_TRACING_MODULE = SourceModule(
    read_file_str('./profiling/kernels/adjust_points_in_mesh.cu')
).get_function("adjust_point_in_mesh")
