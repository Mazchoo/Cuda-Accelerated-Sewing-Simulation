""" Common place to put all parameters of simulation """

NR_STEPS = 200  # Number of time steps to simulate for a sample
AVATAR_SCALING = 0.7  # Amount to change avatar by
VERTEX_RESOLUTION = 1  # Resolution to take number of points
GRAVITY = 9.81  # Acceleration downwards due to gravity
TERMINAL_VELOCITY = 20.0  # Terminal velocity from tensile forces
TIME_DELTA = 0.01  # Time increment to make update to each piece
STRESS_WEIGHTING = 600  # Weight to apply to the stress force
STRESS_THRESHOLD = 0.1  # Percentage of resting distance where stress starts applying
SHEAR_WEIGHTING = 600  # Weight to apply to the shear force
SHEAR_THRESHOLD = 0.1  # Percentage of resting distance where shear starts applying
BEND_WEIGHTING = 600  # Weight to apply to bend force
BEND_THRESHOLD = 0.1  # Sin of angle where bending is applied
CM_PER_M = 100  # Scale of coordinates in clothing to world coordinates
VELOCITY_DAMPING_START = 1.0  # Amount to reduce velocity by in every step at the beginning
VELOCITY_DAMPING_END = 0.0  # Amount to reduce velocity by in every step at the end
DISTANCE_FROM_BODY = 0.025  # Default distance along normal of alignment point on avatar
SEWING_SPACING = 0.01  # Spacing between two points while doing sewing
SEWING_ADJUSTMENT_STEP = 0.01  # Maximum distance per second to get closer to sewing adjustment
WRAP_RADIANS = 0.4  # angle in radians to rotate point when attempting to wrap

DEFAULT_BLOCK_SIZE = 1024  # Default cuda block size
COLLISION_BLOCK_SIZE = 64  # Block size for ray tracing algorithm
